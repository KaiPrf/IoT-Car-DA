#!/usr/bin/env python3

import logging
import math
import threading
import time

import cv2
import rclpy

from cv_bridge import CvBridge
from flask import Flask, Response, jsonify, request
from geometry_msgs.msg import TwistStamped
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from std_msgs.msg import Bool, Float32, Float64


HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="de">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="
            width=device-width,
            initial-scale=1.0,
            maximum-scale=1.0,
            user-scalable=no
        "
    >

    <title>IoT-Car</title>

    <style>

        * {
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
            user-select: none;
        }

        html,
        body {
            margin: 0;
            padding: 0;

            width: 100%;
            height: 100%;

            overflow: hidden;

            background: #000;
            color: #fff;

            font-family:
                system-ui,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

            touch-action: none;
        }

        #app {
            position: fixed;
            inset: 0;

            width: 100%;
            height: 100%;

            overflow: hidden;

            background: #000;
        }


        /* ===================================================== */
        /* CAMERA                                                */
        /* ===================================================== */

        #cameraFeed {
            position: absolute;
            inset: 0;

            width: 100%;
            height: 100%;

            object-fit: cover;

            background: #000;
        }

        #cameraShade {
            position: absolute;
            inset: 0;

            pointer-events: none;

            background:
                linear-gradient(
                    to top,
                    rgba(0, 0, 0, 0.22),
                    rgba(0, 0, 0, 0.01) 45%,
                    rgba(0, 0, 0, 0.09)
                );
        }


        /* ===================================================== */
        /* GLASS                                                 */
        /* ===================================================== */

        .glass {
            background:
                rgba(
                    15,
                    19,
                    25,
                    0.36
                );

            backdrop-filter: blur(9px);
            -webkit-backdrop-filter: blur(9px);

            border:
                1px solid
                rgba(
                    255,
                    255,
                    255,
                    0.12
                );

            box-shadow:
                0 6px 22px
                rgba(
                    0,
                    0,
                    0,
                    0.20
                );
        }


        /* ===================================================== */
        /* TOP LEFT                                              */
        /* ===================================================== */

        #fullscreenButton {
            position: absolute;

            top: 10px;
            left: 10px;

            z-index: 80;

            width: 42px;
            height: 42px;

            padding: 0;

            border: 0;
            border-radius: 12px;

            color: #fff;

            font-size: 20px;
        }

        #connection {
            position: absolute;

            top: 10px;
            left: 60px;

            z-index: 75;

            padding: 8px 11px;

            border-radius: 12px;

            font-size: 11px;
            font-weight: 700;
        }


        /* ===================================================== */
        /* HUD                                                   */
        /* ===================================================== */

        #hudArea {
            position: absolute;

            top: 10px;
            right: 10px;

            z-index: 80;

            display: flex;
            align-items: flex-start;

            gap: 7px;
        }

        #hudButton {
            width: 42px;
            height: 42px;

            padding: 0;

            border: 0;
            border-radius: 12px;

            color: #fff;

            font-size: 18px;
        }

        #hud {
            width: min(225px, 27vw);

            padding: 9px;

            border-radius: 14px;

            transition:
                opacity 0.18s ease,
                transform 0.18s ease;
        }

        #hud.hidden {
            opacity: 0;

            transform:
                translateX(
                    calc(
                        100%
                        +
                        15px
                    )
                );

            pointer-events: none;
        }

        .hudTitle {
            margin-bottom: 7px;

            font-size: 12px;
            font-weight: 800;
        }

        .sensorRow {
            display: flex;

            align-items: center;
            justify-content: space-between;

            gap: 8px;

            padding: 6px 8px;

            margin-bottom: 5px;

            border-radius: 9px;

            background:
                rgba(
                    255,
                    255,
                    255,
                    0.065
                );
        }

        .sensorLabel {
            font-size: 10px;

            color:
                rgba(
                    255,
                    255,
                    255,
                    0.68
                );
        }

        .sensorValue {
            font-size: 15px;
            font-weight: 800;

            text-align: right;
        }

        #distanceInfo {
            font-size: 9px;

            color:
                rgba(
                    255,
                    255,
                    255,
                    0.58
                );

            text-align: right;
        }

        .sliderBox {
            padding: 6px 8px;

            border-radius: 9px;

            background:
                rgba(
                    255,
                    255,
                    255,
                    0.065
                );
        }

        .sliderHeader {
            display: flex;

            justify-content: space-between;

            gap: 6px;

            margin-bottom: 4px;

            font-size: 9px;
        }

        #speedSlider {
            width: 100%;
            height: 18px;
        }


        /* ===================================================== */
        /* STEERING                                              */
        /* ===================================================== */

        #steeringArea {
            position: absolute;

            left: 18px;
            bottom: 16px;

            z-index: 90;

            width:
                min(
                    37vw,
                    330px
                );

            height:
                min(
                    25vh,
                    145px
                );

            border-radius: 75px;

            touch-action: none;
        }

        #steeringBase {
            position: absolute;
            inset: 0;

            border-radius: 75px;

            background:
                rgba(
                    10,
                    14,
                    20,
                    0.25
                );

            border:
                2px solid
                rgba(
                    255,
                    255,
                    255,
                    0.12
                );
        }

        #steeringLine {
            position: absolute;

            left: 13%;
            right: 13%;
            top: 50%;

            height: 2px;

            background:
                rgba(
                    255,
                    255,
                    255,
                    0.13
                );
        }

        #centerMark {
            position: absolute;

            left: 50%;
            top: 27%;

            width: 2px;
            height: 46%;

            background:
                rgba(
                    255,
                    255,
                    255,
                    0.13
                );
        }

        .steeringArrow {
            position: absolute;

            top: 50%;

            transform:
                translateY(-50%);

            font-size: 21px;
            font-weight: 800;

            color:
                rgba(
                    255,
                    255,
                    255,
                    0.28
                );

            pointer-events: none;
        }

        #leftArrow {
            left: 14px;
        }

        #rightArrow {
            right: 14px;
        }

        #steeringStick {
            position: absolute;

            left: 50%;
            top: 50%;

            width: 68px;
            height: 68px;

            transform:
                translate(
                    -50%,
                    -50%
                );

            border-radius: 50%;

            background:
                rgba(
                    238,
                    244,
                    253,
                    0.56
                );

            border:
                2px solid
                rgba(
                    255,
                    255,
                    255,
                    0.30
                );

            box-shadow:
                0 7px 18px
                rgba(
                    0,
                    0,
                    0,
                    0.28
                );

            pointer-events: none;
        }

        #steeringText {
            position: absolute;

            left: 18px;

            bottom:
                calc(
                    min(
                        25vh,
                        145px
                    )
                    +
                    25px
                );

            z-index: 90;

            padding: 6px 10px;

            border-radius: 10px;

            font-size: 10px;
            font-weight: 700;
        }


        /* ===================================================== */
        /* PEDALS                                                */
        /* ===================================================== */

        #pedalArea {
            position: absolute;

            right: 18px;
            bottom: 16px;

            z-index: 90;

            display: flex;

            align-items: flex-end;

            gap: 11px;
        }

        .pedal {
            display: flex;
            flex-direction: column;

            align-items: center;
            justify-content: center;

            width:
                min(
                    11vw,
                    92px
                );

            height:
                min(
                    20vh,
                    110px
                );

            min-width: 68px;
            min-height: 85px;

            padding: 6px;

            border:
                2px solid
                rgba(
                    255,
                    255,
                    255,
                    0.14
                );

            border-radius: 21px;

            color: #fff;

            font-weight: 800;

            touch-action: none;

            transition:
                transform 0.05s ease,
                background 0.05s ease;
        }

        .pedal.active {
            transform:
                scale(0.94);
        }

        #brakeButton {
            background:
                rgba(
                    145,
                    38,
                    45,
                    0.38
                );
        }

        #brakeButton.active {
            background:
                rgba(
                    210,
                    47,
                    57,
                    0.67
                );
        }

        #gasButton {
            height:
                min(
                    23vh,
                    125px
                );

            background:
                rgba(
                    32,
                    130,
                    70,
                    0.38
                );
        }

        #gasButton.active {
            background:
                rgba(
                    38,
                    181,
                    92,
                    0.68
                );
        }

        .pedalMain {
            font-size: 15px;
        }

        .pedalSub {
            margin-top: 3px;

            font-size: 8px;

            opacity: 0.68;
        }


        /* ===================================================== */
        /* PORTRAIT                                              */
        /* ===================================================== */

        #rotateMessage {
            display: none;

            position: absolute;
            inset: 0;

            z-index: 1000;

            background:
                rgba(
                    0,
                    0,
                    0,
                    0.95
                );

            align-items: center;
            justify-content: center;

            padding: 30px;

            text-align: center;

            font-size: 22px;
            font-weight: 700;
        }

        @media (orientation: portrait) {

            #rotateMessage {
                display: flex;
            }

        }

        @media (max-height: 500px) {

            #hud {
                width: 205px;
            }

            .hudTitle {
                display: none;
            }

            .sensorRow {
                padding: 4px 7px;
                margin-bottom: 3px;
            }

            .sensorValue {
                font-size: 13px;
            }

            #steeringArea {
                height: 112px;
            }

            .pedal {
                height: 88px;
            }

            #gasButton {
                height: 98px;
            }

        }

        button {
            cursor: pointer;
        }

    </style>

</head>


<body>

<div id="app">

    <img
        id="cameraFeed"
        src="/video_feed"
        alt="Frontkamera"
    >

    <div id="cameraShade"></div>


    <button
        id="fullscreenButton"
        class="glass"
        type="button"
    >
        ⛶
    </button>


    <div
        id="connection"
        class="glass"
    >
        Verbinde...
    </div>


    <div id="hudArea">

        <button
            id="hudButton"
            class="glass"
            type="button"
        >
            ☰
        </button>


        <div
            id="hud"
            class="glass"
        >

            <div class="hudTitle">
                Fahrzeugdaten
            </div>


            <div class="sensorRow">

                <div class="sensorLabel">
                    Speed
                </div>

                <div
                    id="speedKmh"
                    class="sensorValue"
                >
                    0.00 km/h
                </div>

            </div>


            <div class="sensorRow">

                <div class="sensorLabel">
                    Abstand
                </div>

                <div>

                    <div
                        id="distance"
                        class="sensorValue"
                    >
                        --
                    </div>

                    <div id="distanceInfo">
                        Warte...
                    </div>

                </div>

            </div>


            <div class="sliderBox">

                <div class="sliderHeader">

                    <span>
                        Limit
                    </span>

                    <span id="speedLimitText">
                        4.0 km/h
                    </span>

                </div>


                <input
                    id="speedSlider"
                    type="range"
                    min="0.5"
                    max="10"
                    step="0.5"
                    value="4"
                >

            </div>

        </div>

    </div>


    <div
        id="steeringText"
        class="glass"
    >
        Lenkung 0 %
    </div>


    <div id="steeringArea">

        <div
            id="steeringBase"
            class="glass"
        ></div>

        <div id="steeringLine"></div>

        <div id="centerMark"></div>

        <div
            id="leftArrow"
            class="steeringArrow"
        >
            ◀
        </div>

        <div
            id="rightArrow"
            class="steeringArrow"
        >
            ▶
        </div>

        <div id="steeringStick"></div>

    </div>


    <div id="pedalArea">

        <button
            id="brakeButton"
            class="pedal glass"
            type="button"
        >

            <span class="pedalMain">
                BREMSE
            </span>

            <span class="pedalSub">
                HALTEN = R
            </span>

        </button>


        <button
            id="gasButton"
            class="pedal glass"
            type="button"
        >

            <span class="pedalMain">
                GAS
            </span>

            <span class="pedalSub">
                HALTEN
            </span>

        </button>

    </div>


    <div id="rotateMessage">
        Handy bitte ins Querformat drehen.
    </div>

</div>


<script>

    const steeringArea =
        document.getElementById(
            "steeringArea"
        );

    const steeringStick =
        document.getElementById(
            "steeringStick"
        );

    const steeringText =
        document.getElementById(
            "steeringText"
        );

    const gasButton =
        document.getElementById(
            "gasButton"
        );

    const brakeButton =
        document.getElementById(
            "brakeButton"
        );

    const speedSlider =
        document.getElementById(
            "speedSlider"
        );

    const speedLimitText =
        document.getElementById(
            "speedLimitText"
        );

    const hud =
        document.getElementById(
            "hud"
        );

    const hudButton =
        document.getElementById(
            "hudButton"
        );

    const fullscreenButton =
        document.getElementById(
            "fullscreenButton"
        );


    let steeringActive = false;

    let steering = 0.0;

    let gasPressed = false;
    let brakePressed = false;

    let hudVisible = true;


    function clamp(
        value,
        minimum,
        maximum
    ) {

        return Math.max(
            minimum,
            Math.min(
                maximum,
                value
            )
        );
    }


    function deadzone(
        value,
        zone
    ) {

        const magnitude =
            Math.abs(value);


        if (
            magnitude
            <=
            zone
        ) {

            return 0.0;
        }


        const normalized =
            (
                magnitude
                -
                zone
            )
            /
            (
                1.0
                -
                zone
            );


        return (
            Math.sign(value)
            *
            normalized
        );
    }


    function steeringCurve(
        value
    ) {

        return (
            Math.sign(value)
            *
            Math.pow(
                Math.abs(value),
                1.35
            )
        );
    }


    function updateSteeringVisual() {

        const rect =
            steeringArea
            .getBoundingClientRect();


        const maxTravel =
            rect.width
            /
            2
            -
            42;


        const x =
            steering
            *
            maxTravel;


        steeringStick
            .style
            .transform =
                "translate("
                +
                "calc(-50% + "
                +
                x
                +
                "px), "
                +
                "-50%"
                +
                ")";


        steeringText
            .textContent =
                "Lenkung "
                +
                Math.round(
                    steering
                    *
                    100
                )
                +
                " %";
    }


    function updateSteering(
        clientX
    ) {

        const rect =
            steeringArea
            .getBoundingClientRect();


        const centerX =
            rect.left
            +
            rect.width / 2;


        const maxTravel =
            rect.width
            /
            2
            -
            42;


        let raw =
            (
                clientX
                -
                centerX
            )
            /
            maxTravel;


        raw =
            clamp(
                raw,
                -1.0,
                1.0
            );


        raw =
            deadzone(
                raw,
                0.06
            );


        steering =
            steeringCurve(
                raw
            );


        updateSteeringVisual();
    }


    function centerSteering() {

        steeringActive =
            false;

        steering =
            0.0;

        updateSteeringVisual();
    }


    steeringArea
        .addEventListener(
            "pointerdown",
            function(event) {

                steeringActive =
                    true;


                steeringArea
                    .setPointerCapture(
                        event.pointerId
                    );


                updateSteering(
                    event.clientX
                );
            }
        );


    steeringArea
        .addEventListener(
            "pointermove",
            function(event) {

                if (
                    !steeringActive
                ) {

                    return;
                }


                updateSteering(
                    event.clientX
                );
            }
        );


    steeringArea
        .addEventListener(
            "pointerup",
            centerSteering
        );


    steeringArea
        .addEventListener(
            "pointercancel",
            centerSteering
        );


    function setGas(
        value
    ) {

        gasPressed =
            value;


        gasButton
            .classList
            .toggle(
                "active",
                value
            );
    }


    function setBrake(
        value
    ) {

        brakePressed =
            value;


        brakeButton
            .classList
            .toggle(
                "active",
                value
            );
    }


    gasButton
        .addEventListener(
            "pointerdown",
            function(event) {

                gasButton
                    .setPointerCapture(
                        event.pointerId
                    );


                setGas(
                    true
                );
            }
        );


    gasButton
        .addEventListener(
            "pointerup",
            function() {

                setGas(
                    false
                );
            }
        );


    gasButton
        .addEventListener(
            "pointercancel",
            function() {

                setGas(
                    false
                );
            }
        );


    brakeButton
        .addEventListener(
            "pointerdown",
            function(event) {

                brakeButton
                    .setPointerCapture(
                        event.pointerId
                    );


                setBrake(
                    true
                );
            }
        );


    brakeButton
        .addEventListener(
            "pointerup",
            function() {

                setBrake(
                    false
                );
            }
        );


    brakeButton
        .addEventListener(
            "pointercancel",
            function() {

                setBrake(
                    false
                );
            }
        );


    speedSlider
        .addEventListener(
            "input",
            function() {

                speedLimitText
                    .textContent =
                        Number(
                            speedSlider
                            .value
                        )
                        .toFixed(
                            1
                        )
                        +
                        " km/h";
            }
        );


    hudButton
        .addEventListener(
            "click",
            function() {

                hudVisible =
                    !hudVisible;


                hud
                    .classList
                    .toggle(
                        "hidden",
                        !hudVisible
                    );


                hudButton
                    .textContent =
                        hudVisible
                        ?
                        "☰"
                        :
                        "›";
            }
        );


    fullscreenButton
        .addEventListener(
            "click",
            async function() {

                try {

                    if (
                        !document
                        .fullscreenElement
                    ) {

                        await document
                            .documentElement
                            .requestFullscreen();


                        if (
                            screen.orientation
                            &&
                            screen.orientation.lock
                        ) {

                            try {

                                await screen
                                    .orientation
                                    .lock(
                                        "landscape"
                                    );

                            } catch (
                                error
                            ) {
                            }
                        }

                    } else {

                        await document
                            .exitFullscreen();
                    }

                } catch (
                    error
                ) {

                    console.log(
                        error
                    );
                }
            }
        );


    async function sendControl() {

        try {

            await fetch(
                "/api/control",
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            steering:
                                steering,

                            gas:
                                gasPressed,

                            brake:
                                brakePressed,

                            max_speed_kmh:
                                Number(
                                    speedSlider
                                    .value
                                )

                        })
                }
            );

        } catch (
            error
        ) {
        }
    }


    async function updateState() {

        try {

            const response =
                await fetch(
                    "/api/state",
                    {
                        cache:
                            "no-store"
                    }
                );


            const state =
                await response
                .json();


            document
                .getElementById(
                    "speedKmh"
                )
                .textContent =
                    Number(
                        state.speed_kmh
                    )
                    .toFixed(
                        2
                    )
                    +
                    " km/h";


            const distanceElement =
                document
                .getElementById(
                    "distance"
                );


            const distanceInfo =
                document
                .getElementById(
                    "distanceInfo"
                );


            if (
                !state
                .distance_valid
            ) {

                distanceElement
                    .textContent =
                        "--";


                distanceInfo
                    .textContent =
                        "Kein Hindernis";

            } else if (
                state.distance
                <=
                0.02
            ) {

                distanceElement
                    .textContent =
                        "0.00 m";


                distanceInfo
                    .textContent =
                        "Direkt voraus";

            } else {

                distanceElement
                    .textContent =
                        Number(
                            state.distance
                        )
                        .toFixed(
                            2
                        )
                        +
                        " m";


                distanceInfo
                    .textContent =
                        "Erkannt";
            }


            document
                .getElementById(
                    "connection"
                )
                .textContent =
                    "ROS verbunden";

        } catch (
            error
        ) {

            document
                .getElementById(
                    "connection"
                )
                .textContent =
                    "Keine Verbindung";
        }
    }


    function releaseControls() {

        steering =
            0.0;

        gasPressed =
            false;

        brakePressed =
            false;


        setGas(
            false
        );


        setBrake(
            false
        );


        updateSteeringVisual();


        navigator
            .sendBeacon(
                "/api/stop"
            );
    }


    updateSteeringVisual();


    setInterval(
        updateState,
        200
    );


    setInterval(
        sendControl,
        50
    );


    document
        .addEventListener(
            "visibilitychange",
            function() {

                if (
                    document.hidden
                ) {

                    releaseControls();
                }
            }
        );


    window
        .addEventListener(
            "beforeunload",
            releaseControls
        );

</script>

</body>

</html>
"""


class WebControlNode(Node):

    def __init__(self):

        super().__init__(
            'web_control'
        )


        logging.getLogger(
            'werkzeug'
        ).setLevel(
            logging.ERROR
        )


        # =========================================================
        # CAMERA
        # =========================================================

        self.cv_bridge = (
            CvBridge()
        )


        self.latest_jpeg = None
        self.frame_number = 0


        self.image_lock = (
            threading.Lock()
        )


        # =========================================================
        # ROS
        # =========================================================

        self.command_pub = (
            self.create_publisher(
                TwistStamped,
                '/ackermann_steering_controller/reference',
                10
            )
        )


        self.speed_kmh_sub = (
            self.create_subscription(
                Float64,
                '/car/speed_kmh',
                self.speed_kmh_callback,
                10
            )
        )


        self.speed_ms_sub = (
            self.create_subscription(
                Float64,
                '/car/speed',
                self.speed_ms_callback,
                10
            )
        )


        self.distance_sub = (
            self.create_subscription(
                Float32,
                '/car/distance',
                self.distance_callback,
                10
            )
        )


        self.distance_valid_sub = (
            self.create_subscription(
                Bool,
                '/car/distance_valid',
                self.distance_valid_callback,
                10
            )
        )


        self.camera_sub = (
            self.create_subscription(
                Image,
                '/car/camera/image',
                self.camera_callback,
                qos_profile_sensor_data
            )
        )


        # =========================================================
        # SENSOR STATUS
        # =========================================================

        self.speed_kmh = 0.0
        self.speed_ms = 0.0

        self.distance = 4.0
        self.distance_valid = False


        # =========================================================
        # INPUT
        # =========================================================

        self.target_steering = 0.0

        self.gas_pressed = False
        self.brake_pressed = False

        self.brake_press_time = None

        self.max_speed_kmh = 4.0

        self.last_control_time = (
            time.monotonic()
        )


        # =========================================================
        # INTERNAL VEHICLE STATE
        # =========================================================

        self.current_steering = 0.0
        self.command_speed = 0.0


        self.state_lock = (
            threading.Lock()
        )


        # =========================================================
        # VEHICLE GEOMETRY
        # =========================================================

        self.wheelbase = 0.26

        # Rund 28.6 Grad voller Lenkeinschlag
        self.max_steering_angle = 0.50


        # =========================================================
        # GAME / SIMCADE SETTINGS
        # =========================================================

        # Sehr schnelle Lenkreaktion.
        self.steering_rate = 8.0

        # Beschleunigung in m/s².
        self.acceleration_rate = 2.4

        # Gas loslassen.
        self.coast_deceleration = 1.5

        # Bremspedal.
        self.brake_deceleration = 5.0

        # Rückwärtsbeschleunigung.
        self.reverse_acceleration = 2.0

        # Rückwärts maximal 60 % des Speed-Limits.
        self.reverse_speed_factor = 0.60

        # Bremse nach Stillstand so lange halten,
        # bevor Rückwärtsfahrt beginnt.
        self.reverse_delay = 0.40

        # Cornering Assist:
        # Bei vollem Lenkeinschlag bleiben noch
        # 35 % der eingestellten Maximalgeschwindigkeit.
        self.minimum_corner_speed_factor = 0.35

        # Stärke der Cornering-Speed-Kurve.
        self.cornering_strength = 0.65

        # Wie schnell das Auto beim starken Einlenken
        # auf die Cornering-Speed abbremst.
        self.corner_deceleration = 4.0

        # Steuerdaten-Timeout.
        self.control_timeout = 0.40

        self.control_period = 0.05


        # =========================================================
        # TIMER
        # =========================================================

        self.command_timer = (
            self.create_timer(
                self.control_period,
                self.publish_command
            )
        )


        # =========================================================
        # FLASK
        # =========================================================

        self.app = Flask(
            __name__
        )


        self.setup_routes()


        self.get_logger().info(
            'Simcade web control started'
        )


    # =============================================================
    # SENSOR CALLBACKS
    # =============================================================

    def speed_kmh_callback(
        self,
        msg
    ):

        with self.state_lock:

            self.speed_kmh = round(
                float(
                    msg.data
                ),
                2
            )


    def speed_ms_callback(
        self,
        msg
    ):

        with self.state_lock:

            self.speed_ms = round(
                float(
                    msg.data
                ),
                3
            )


    def distance_callback(
        self,
        msg
    ):

        with self.state_lock:

            self.distance = round(
                float(
                    msg.data
                ),
                3
            )


    def distance_valid_callback(
        self,
        msg
    ):

        with self.state_lock:

            self.distance_valid = bool(
                msg.data
            )


    def camera_callback(
        self,
        msg
    ):

        try:

            frame = (
                self.cv_bridge
                .imgmsg_to_cv2(
                    msg,
                    desired_encoding='bgr8'
                )
            )


            success, encoded = (
                cv2.imencode(
                    '.jpg',
                    frame,
                    [
                        int(
                            cv2.IMWRITE_JPEG_QUALITY
                        ),
                        82
                    ]
                )
            )


            if (
                not success
            ):

                return


            with self.image_lock:

                self.latest_jpeg = (
                    encoded
                    .tobytes()
                )


                self.frame_number += 1


        except Exception as exception:

            self.get_logger().warning(
                'Camera conversion failed: '
                +
                str(
                    exception
                )
            )


    # =============================================================
    # WEB INPUT
    # =============================================================

    def set_control(
        self,
        steering,
        gas,
        brake,
        max_speed_kmh
    ):

        steering = max(
            -1.0,
            min(
                1.0,
                steering
            )
        )


        max_speed_kmh = max(
            0.5,
            min(
                10.0,
                max_speed_kmh
            )
        )


        now = (
            time.monotonic()
        )


        with self.state_lock:

            was_braking = (
                self.brake_pressed
            )


            self.target_steering = (
                steering
            )

            self.gas_pressed = bool(
                gas
            )

            self.brake_pressed = bool(
                brake
            )

            self.max_speed_kmh = (
                max_speed_kmh
            )

            self.last_control_time = (
                now
            )


            if (
                self.brake_pressed
                and
                not was_braking
            ):

                self.brake_press_time = (
                    now
                )


            elif (
                not self.brake_pressed
            ):

                self.brake_press_time = (
                    None
                )


    def emergency_stop(
        self
    ):

        with self.state_lock:

            self.target_steering = 0.0

            self.gas_pressed = False
            self.brake_pressed = False

            self.brake_press_time = None

            self.current_steering = 0.0

            self.command_speed = 0.0

            self.last_control_time = (
                time.monotonic()
            )


    # =============================================================
    # HELPERS
    # =============================================================

    def move_towards(
        self,
        current,
        target,
        maximum_change
    ):

        difference = (
            target
            -
            current
        )


        if (
            abs(
                difference
            )
            <=
            maximum_change
        ):

            return target


        if (
            difference
            >
            0.0
        ):

            return (
                current
                +
                maximum_change
            )


        return (
            current
            -
            maximum_change
        )


    # =============================================================
    # CONTROL LOOP
    # =============================================================

    def publish_command(
        self
    ):

        now = (
            time.monotonic()
        )


        with self.state_lock:

            steering_target = (
                self.target_steering
            )

            gas_pressed = (
                self.gas_pressed
            )

            brake_pressed = (
                self.brake_pressed
            )

            brake_press_time = (
                self.brake_press_time
            )

            max_speed_kmh = (
                self.max_speed_kmh
            )

            last_control_time = (
                self.last_control_time
            )

            measured_speed = (
                self.speed_ms
            )

            current_steering = (
                self.current_steering
            )

            command_speed = (
                self.command_speed
            )


        # ---------------------------------------------------------
        # CONNECTION TIMEOUT
        # ---------------------------------------------------------

        if (
            now
            -
            last_control_time
            >
            self.control_timeout
        ):

            steering_target = 0.0

            gas_pressed = False
            brake_pressed = False

            brake_press_time = None


        # ---------------------------------------------------------
        # STEERING
        #
        # Keine Geschwindigkeitsreduktion des Lenkwinkels mehr.
        # Voller Lenkeinschlag bleibt voller Lenkeinschlag.
        # ---------------------------------------------------------

        steering_step = (
            self.steering_rate
            *
            self.control_period
        )


        current_steering = (
            self.move_towards(
                current_steering,
                steering_target,
                steering_step
            )
        )


        # ---------------------------------------------------------
        # SPEED LIMITS
        # ---------------------------------------------------------

        base_forward_limit = (
            max_speed_kmh
            /
            3.6
        )


        reverse_speed_limit = (
            base_forward_limit
            *
            self.reverse_speed_factor
        )


        # ---------------------------------------------------------
        # CORNERING ASSIST
        #
        # Statt bei Geschwindigkeit die Lenkung wegzunehmen,
        # reduzieren wir bei starkem Einlenken die Zielgeschw.
        #
        # steering 0.0 -> 100 % Speed
        # steering 1.0 -> 35 % Speed
        # ---------------------------------------------------------

        steering_amount = min(
            abs(
                current_steering
            ),
            1.0
        )


        corner_speed_factor = (
            1.0
            -
            (
                self.cornering_strength
                *
                (
                    steering_amount
                    **
                    1.35
                )
            )
        )


        corner_speed_factor = max(
            self.minimum_corner_speed_factor,
            corner_speed_factor
        )


        corner_forward_limit = (
            base_forward_limit
            *
            corner_speed_factor
        )


        # ---------------------------------------------------------
        # DRIVER INPUT
        # ---------------------------------------------------------

        desired_speed = 0.0

        mode = "coast"


        if (
            gas_pressed
            and
            brake_pressed
        ):

            desired_speed = 0.0

            mode = "brake"


        elif (
            gas_pressed
        ):

            desired_speed = (
                corner_forward_limit
            )

            mode = "accelerate"


        elif (
            brake_pressed
        ):

            brake_held_time = 0.0


            if (
                brake_press_time
                is not None
            ):

                brake_held_time = (
                    now
                    -
                    brake_press_time
                )


            vehicle_is_stopped = (
                abs(
                    measured_speed
                )
                <
                0.10
                and
                abs(
                    command_speed
                )
                <
                0.10
            )


            if (
                not vehicle_is_stopped
            ):

                desired_speed = 0.0

                mode = "brake"


            elif (
                brake_held_time
                >=
                self.reverse_delay
            ):

                desired_speed = (
                    -reverse_speed_limit
                )

                mode = "reverse"


            else:

                desired_speed = 0.0

                mode = "brake"


        else:

            desired_speed = 0.0

            mode = "coast"


        # ---------------------------------------------------------
        # SPEED RESPONSE
        # ---------------------------------------------------------

        if (
            mode
            ==
            "accelerate"
        ):

            if (
                command_speed
                >
                desired_speed
            ):

                speed_change = (
                    self.corner_deceleration
                    *
                    self.control_period
                )

            else:

                speed_change = (
                    self.acceleration_rate
                    *
                    self.control_period
                )


        elif (
            mode
            ==
            "reverse"
        ):

            speed_change = (
                self.reverse_acceleration
                *
                self.control_period
            )


        elif (
            mode
            ==
            "brake"
        ):

            speed_change = (
                self.brake_deceleration
                *
                self.control_period
            )


        else:

            speed_change = (
                self.coast_deceleration
                *
                self.control_period
            )


        command_speed = (
            self.move_towards(
                command_speed,
                desired_speed,
                speed_change
            )
        )


        # ---------------------------------------------------------
        # FULL STEERING ANGLE
        #
        # Kein Speed Scaling.
        # ---------------------------------------------------------

        steering_angle = (
            -current_steering
            *
            self.max_steering_angle
        )


        # ---------------------------------------------------------
        # BODY YAW RATE
        # ---------------------------------------------------------

        if (
            abs(
                command_speed
            )
            <
            0.001
        ):

            angular_speed = 0.0


        else:

            angular_speed = (
                command_speed
                *
                math.tan(
                    steering_angle
                )
                /
                self.wheelbase
            )


        # ---------------------------------------------------------
        # PUBLISH
        # ---------------------------------------------------------

        command = (
            TwistStamped()
        )


        command.header.stamp = (
            self.get_clock()
            .now()
            .to_msg()
        )


        command.header.frame_id = (
            'base_link'
        )


        command.twist.linear.x = float(
            command_speed
        )


        command.twist.angular.z = float(
            angular_speed
        )


        self.command_pub.publish(
            command
        )


        with self.state_lock:

            self.current_steering = (
                current_steering
            )

            self.command_speed = (
                command_speed
            )


    # =============================================================
    # WEB ROUTES
    # =============================================================

    def setup_routes(
        self
    ):


        @self.app.route('/')

        def index():

            return HTML_PAGE


        @self.app.route(
            '/api/state'
        )

        def api_state():

            with self.state_lock:

                result = {

                    'speed_kmh':
                        self.speed_kmh,

                    'speed_ms':
                        self.speed_ms,

                    'distance':
                        self.distance,

                    'distance_valid':
                        self.distance_valid,

                    'max_speed_kmh':
                        self.max_speed_kmh

                }


            response = jsonify(
                result
            )


            response.headers[
                'Cache-Control'
            ] = (
                'no-store'
            )


            return response


        @self.app.route(
            '/api/control',
            methods=['POST']
        )

        def api_control():

            data = request.get_json(
                silent=True
            )


            if (
                data is None
            ):

                return jsonify({
                    'ok': False
                }), 400


            try:

                steering = float(
                    data.get(
                        'steering',
                        0.0
                    )
                )


                gas = bool(
                    data.get(
                        'gas',
                        False
                    )
                )


                brake = bool(
                    data.get(
                        'brake',
                        False
                    )
                )


                max_speed_kmh = float(
                    data.get(
                        'max_speed_kmh',
                        4.0
                    )
                )


            except (
                ValueError,
                TypeError
            ):

                return jsonify({
                    'ok': False
                }), 400


            self.set_control(
                steering,
                gas,
                brake,
                max_speed_kmh
            )


            return jsonify({
                'ok': True
            })


        @self.app.route(
            '/api/stop',
            methods=['POST']
        )

        def stop():

            self.emergency_stop()


            return jsonify({
                'ok': True
            })


        @self.app.route(
            '/video_feed'
        )

        def video_feed():

            return Response(
                self.generate_stream(),

                mimetype=(
                    'multipart/'
                    'x-mixed-replace; '
                    'boundary=frame'
                ),

                headers={

                    'Cache-Control':
                        'no-store, '
                        'no-cache, '
                        'must-revalidate, '
                        'max-age=0',

                    'Pragma':
                        'no-cache',

                    'X-Accel-Buffering':
                        'no'

                }
            )


    # =============================================================
    # MJPEG
    # =============================================================

    def generate_stream(
        self
    ):

        last_frame_number = -1


        while rclpy.ok():

            with self.image_lock:

                jpeg = (
                    self.latest_jpeg
                )

                frame_number = (
                    self.frame_number
                )


            if (
                jpeg is None
            ):

                time.sleep(
                    0.02
                )

                continue


            if (
                frame_number
                ==
                last_frame_number
            ):

                time.sleep(
                    0.006
                )

                continue


            last_frame_number = (
                frame_number
            )


            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n'
                b'Cache-Control: no-cache\r\n'
                b'\r\n'
                +
                jpeg
                +
                b'\r\n'
            )


    # =============================================================
    # SERVER
    # =============================================================

    def run_web_server(
        self
    ):

        self.app.run(
            host='0.0.0.0',
            port=8080,
            threaded=True,
            use_reloader=False
        )


def main(
    args=None
):

    rclpy.init(
        args=args
    )


    node = (
        WebControlNode()
    )


    web_thread = (
        threading.Thread(
            target=
                node.run_web_server,

            daemon=True
        )
    )


    web_thread.start()


    try:

        rclpy.spin(
            node
        )


    except KeyboardInterrupt:

        pass


    node.emergency_stop()

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':

    main()
