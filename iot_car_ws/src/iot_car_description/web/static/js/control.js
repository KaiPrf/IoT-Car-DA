const state = {
    steering: 0.0,
    throttle: 0.0,
    brake: 0.0,
    emergencyStop: false,
};

let controlWebSocket = null;
let cameraWebSocket = null;
let telemetryWebSocket = null;

let controlReconnectTimer = null;
let cameraReconnectTimer = null;
let telemetryReconnectTimer = null;

let steeringPointer = null;
let steeringVisualPosition = 0.5;

let cameraDecodeBusy = false;
let pendingCameraFrame = null;

const body =
    document.body;

const touchStage =
    document.getElementById(
        "touch-stage"
    );

const steeringPad =
    document.getElementById(
        "steering-pad"
    );

const steeringMarker =
    document.getElementById(
        "steering-marker"
    );

const gasButton =
    document.getElementById(
        "gas-button"
    );

const brakeButton =
    document.getElementById(
        "brake-button"
    );

const fullscreenButton =
    document.getElementById(
        "fullscreen-button"
    );

const connectionStatus =
    document.getElementById(
        "connection-status"
    );

const cameraStatus =
    document.getElementById(
        "camera-status"
    );

const controlMode =
    document.getElementById(
        "control-mode"
    );

const desktopCamera =
    document.getElementById(
        "desktop-camera"
    );

const touchCamera =
    document.getElementById(
        "touch-camera"
    );

const keyW =
    document.getElementById("key-w");

const keyA =
    document.getElementById("key-a");

const keyS =
    document.getElementById("key-s");

const keyD =
    document.getElementById("key-d");

const spaceKey =
    document.getElementById(
        "space-key"
    );

const pressedKeys =
    new Set();


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


function detectControlMode() {
    const coarsePointer =
        window.matchMedia(
            "(pointer: coarse)"
        ).matches;

    if (coarsePointer) {
        body.classList.remove(
            "desktop-mode"
        );

        body.classList.add(
            "touch-mode"
        );

        controlMode.textContent =
            "Touch-Steuerung";

    } else {
        body.classList.remove(
            "touch-mode"
        );

        body.classList.add(
            "desktop-mode"
        );

        controlMode.textContent =
            "PC / Tastatur";
    }
}


function updateTouchDisplay() {
    steeringMarker.style.left =
        `${steeringVisualPosition * 100}%`;

    gasButton.classList.toggle(
        "active",
        state.throttle > 0.0
    );

    brakeButton.classList.toggle(
        "active",
        state.brake > 0.0
    );
}


function updateKeyboardDisplay() {
    const left =
        pressedKeys.has("KeyA")
        || pressedKeys.has("ArrowLeft");

    const right =
        pressedKeys.has("KeyD")
        || pressedKeys.has("ArrowRight");

    const gas =
        pressedKeys.has("KeyW")
        || pressedKeys.has("ArrowUp");

    const brake =
        pressedKeys.has("KeyS")
        || pressedKeys.has("ArrowDown");

    keyW.classList.toggle(
        "active",
        gas
    );

    keyA.classList.toggle(
        "active",
        left
    );

    keyS.classList.toggle(
        "active",
        brake
    );

    keyD.classList.toggle(
        "active",
        right
    );

    spaceKey.classList.toggle(
        "active",
        pressedKeys.has("Space")
    );
}


function updateDisplay() {
    updateTouchDisplay();
    updateKeyboardDisplay();
}


function sendState() {
    if (
        !controlWebSocket
        || controlWebSocket.readyState
            !== WebSocket.OPEN
    ) {
        return;
    }

    controlWebSocket.send(
        JSON.stringify({
            steering:
                state.steering,

            throttle:
                state.throttle,

            brake:
                state.brake,

            emergency_stop:
                state.emergencyStop,
        })
    );
}


function resetControls() {
    pressedKeys.clear();

    state.steering = 0.0;
    state.throttle = 0.0;
    state.brake = 0.0;
    state.emergencyStop = false;

    steeringVisualPosition = 0.5;

    updateDisplay();
    sendState();
}


/* WebSocket-Verbindungen */

function scheduleControlReconnect() {
    if (controlReconnectTimer) {
        return;
    }

    controlReconnectTimer =
        setTimeout(
            () => {
                controlReconnectTimer = null;
                connectControlWebSocket();
            },
            1000
        );
}


function connectControlWebSocket() {
    if (
        controlWebSocket
        && (
            controlWebSocket.readyState
                === WebSocket.OPEN
            || controlWebSocket.readyState
                === WebSocket.CONNECTING
        )
    ) {
        return;
    }

    const protocol =
        location.protocol === "https:"
            ? "wss:"
            : "ws:";

    const socket =
        new WebSocket(
            `${protocol}//${location.host}/ws`
        );

    controlWebSocket = socket;

    socket.addEventListener(
        "open",
        () => {
            if (
                controlWebSocket !== socket
            ) {
                return;
            }

            connectionStatus.textContent =
                "Steuerung verbunden";

            connectionStatus.classList.remove(
                "disconnected"
            );

            connectionStatus.classList.add(
                "connected"
            );
        }
    );

    socket.addEventListener(
        "close",
        () => {
            if (
                controlWebSocket !== socket
            ) {
                return;
            }

            controlWebSocket = null;

            connectionStatus.textContent =
                "Steuerung getrennt";

            connectionStatus.classList.remove(
                "connected"
            );

            connectionStatus.classList.add(
                "disconnected"
            );

            resetControls();
            scheduleControlReconnect();
        }
    );

    socket.addEventListener(
        "error",
        () => {
            socket.close();
        }
    );
}


function scheduleTelemetryReconnect() {
    if (telemetryReconnectTimer) {
        return;
    }

    telemetryReconnectTimer =
        setTimeout(
            () => {
                telemetryReconnectTimer = null;
                connectTelemetryWebSocket();
            },
            1000
        );
}


function connectTelemetryWebSocket() {
    if (
        telemetryWebSocket
        && (
            telemetryWebSocket.readyState
                === WebSocket.OPEN
            || telemetryWebSocket.readyState
                === WebSocket.CONNECTING
        )
    ) {
        return;
    }

    const protocol =
        location.protocol === "https:"
            ? "wss:"
            : "ws:";

    const socket =
        new WebSocket(
            `${protocol}//${location.host}/telemetry-ws`
        );

    telemetryWebSocket = socket;

    socket.addEventListener(
        "message",
        (event) => {
            if (
                telemetryWebSocket !== socket
            ) {
                return;
            }

            try {
                const data =
                    JSON.parse(
                        event.data
                    );

                updateTelemetry(
                    data
                );

            } catch (error) {
            }
        }
    );

    socket.addEventListener(
        "close",
        () => {
            if (
                telemetryWebSocket !== socket
            ) {
                return;
            }

            telemetryWebSocket = null;

            scheduleTelemetryReconnect();
        }
    );

    socket.addEventListener(
        "error",
        () => {
            socket.close();
        }
    );
}


function updateTelemetry(data) {
    let speedText = "--";

    if (
        typeof data.speed_kmh
        === "number"
    ) {
        speedText =
            data.speed_kmh.toFixed(2);
    }

    let distanceText = "--";

    if (
        data.distance_valid
        && typeof data.distance
            === "number"
    ) {
        distanceText =
            `${data.distance.toFixed(2)} m`;

    } else if (
        data.distance !== null
    ) {
        distanceText =
            "Kein Hindernis";
    }

    document.getElementById(
        "touch-speed"
    ).textContent =
        speedText;

    document.getElementById(
        "touch-distance"
    ).textContent =
        distanceText;

    document.getElementById(
        "desktop-speed"
    ).textContent =
        `${speedText} km/h`;

    document.getElementById(
        "desktop-distance"
    ).textContent =
        distanceText;
}


function scheduleCameraReconnect() {
    if (cameraReconnectTimer) {
        return;
    }

    cameraReconnectTimer =
        setTimeout(
            () => {
                cameraReconnectTimer = null;
                connectCameraWebSocket();
            },
            750
        );
}


function connectCameraWebSocket() {
    if (
        cameraWebSocket
        && (
            cameraWebSocket.readyState
                === WebSocket.OPEN
            || cameraWebSocket.readyState
                === WebSocket.CONNECTING
        )
    ) {
        return;
    }

    const protocol =
        location.protocol === "https:"
            ? "wss:"
            : "ws:";

    const socket =
        new WebSocket(
            `${protocol}//${location.host}/camera-ws`
        );

    socket.binaryType =
        "blob";

    cameraWebSocket = socket;

    socket.addEventListener(
        "open",
        () => {
            if (
                cameraWebSocket !== socket
            ) {
                return;
            }

            cameraStatus.textContent =
                "Kamera verbunden";

            cameraStatus.classList.remove(
                "disconnected"
            );

            cameraStatus.classList.add(
                "connected"
            );
        }
    );

    socket.addEventListener(
        "message",
        (event) => {
            if (
                cameraWebSocket !== socket
                || !(event.data instanceof Blob)
            ) {
                return;
            }

            pendingCameraFrame =
                event.data;

            processLatestCameraFrame();
        }
    );

    socket.addEventListener(
        "close",
        () => {
            if (
                cameraWebSocket !== socket
            ) {
                return;
            }

            cameraWebSocket = null;

            pendingCameraFrame = null;
            cameraDecodeBusy = false;

            cameraStatus.textContent =
                "Kamera getrennt";

            cameraStatus.classList.remove(
                "connected"
            );

            cameraStatus.classList.add(
                "disconnected"
            );

            scheduleCameraReconnect();
        }
    );

    socket.addEventListener(
        "error",
        () => {
            socket.close();
        }
    );
}


/* Kamera */

async function processLatestCameraFrame() {
    if (
        cameraDecodeBusy
        || !pendingCameraFrame
    ) {
        return;
    }

    cameraDecodeBusy = true;

    const frame =
        pendingCameraFrame;

    pendingCameraFrame = null;

    try {
        const bitmap =
            await createImageBitmap(
                frame
            );

        drawCameraFrame(
            desktopCamera,
            bitmap
        );

        drawCameraFrame(
            touchCamera,
            bitmap
        );

        bitmap.close();

    } catch (error) {
    }

    cameraDecodeBusy = false;

    if (pendingCameraFrame) {
        processLatestCameraFrame();
    }
}


function drawCameraFrame(
    canvas,
    bitmap
) {
    const rect =
        canvas.getBoundingClientRect();

    if (
        rect.width < 2
        || rect.height < 2
    ) {
        return;
    }

    const ratio =
        Math.min(
            window.devicePixelRatio || 1,
            2
        );

    const width =
        Math.round(
            rect.width * ratio
        );

    const height =
        Math.round(
            rect.height * ratio
        );

    if (
        canvas.width !== width
        || canvas.height !== height
    ) {
        canvas.width = width;
        canvas.height = height;
    }

    const context =
        canvas.getContext(
            "2d",
            {
                alpha: false
            }
        );

    const scale =
        Math.max(
            width / bitmap.width,
            height / bitmap.height
        );

    const sourceWidth =
        width / scale;

    const sourceHeight =
        height / scale;

    context.drawImage(
        bitmap,

        (
            bitmap.width
            - sourceWidth
        ) / 2,

        (
            bitmap.height
            - sourceHeight
        ) / 2,

        sourceWidth,
        sourceHeight,

        0,
        0,
        width,
        height
    );
}


/* Tastatur */

function updateKeyboardState() {
    const left =
        pressedKeys.has("KeyA")
        || pressedKeys.has("ArrowLeft");

    const right =
        pressedKeys.has("KeyD")
        || pressedKeys.has("ArrowRight");

    const gas =
        pressedKeys.has("KeyW")
        || pressedKeys.has("ArrowUp");

    const brake =
        pressedKeys.has("KeyS")
        || pressedKeys.has("ArrowDown");

    if (left && !right) {
        state.steering = 1.0;

    } else if (
        right
        && !left
    ) {
        state.steering = -1.0;

    } else {
        state.steering = 0.0;
    }

    state.throttle =
        gas ? 1.0 : 0.0;

    state.brake =
        brake ? 1.0 : 0.0;

    state.emergencyStop =
        pressedKeys.has("Space");

    updateDisplay();
}


window.addEventListener(
    "keydown",
    (event) => {
        if (
            body.classList.contains(
                "touch-mode"
            )
        ) {
            return;
        }

        const keys = [
            "KeyW",
            "KeyA",
            "KeyS",
            "KeyD",
            "ArrowUp",
            "ArrowDown",
            "ArrowLeft",
            "ArrowRight",
            "Space",
        ];

        if (
            !keys.includes(
                event.code
            )
        ) {
            return;
        }

        event.preventDefault();

        pressedKeys.add(
            event.code
        );

        updateKeyboardState();
    }
);


window.addEventListener(
    "keyup",
    (event) => {
        pressedKeys.delete(
            event.code
        );

        updateKeyboardState();
    }
);


/* Touch-Lenkung */

function setSteeringFromPointer(
    event
) {
    const rect =
        steeringPad.getBoundingClientRect();

    const normalized =
        clamp(
            (
                event.clientX
                - rect.left
            )
            / rect.width,
            0.0,
            1.0
        );

    steeringVisualPosition =
        normalized;

    state.steering =
        (0.5 - normalized) * 2.0;

    updateTouchDisplay();
}


steeringPad.addEventListener(
    "pointerdown",
    (event) => {
        steeringPointer =
            event.pointerId;

        steeringPad.setPointerCapture(
            event.pointerId
        );

        setSteeringFromPointer(
            event
        );
    }
);


steeringPad.addEventListener(
    "pointermove",
    (event) => {
        if (
            steeringPointer
            !== event.pointerId
        ) {
            return;
        }

        setSteeringFromPointer(
            event
        );
    }
);


function releaseSteering(
    event
) {
    if (
        steeringPointer
        !== event.pointerId
    ) {
        return;
    }

    steeringPointer = null;

    steeringVisualPosition = 0.5;
    state.steering = 0.0;

    updateTouchDisplay();
}


steeringPad.addEventListener(
    "pointerup",
    releaseSteering
);

steeringPad.addEventListener(
    "pointercancel",
    releaseSteering
);


function bindPedal(
    button,
    stateName
) {
    button.addEventListener(
        "pointerdown",
        (event) => {
            event.preventDefault();

            button.setPointerCapture(
                event.pointerId
            );

            state[stateName] = 1.0;

            updateTouchDisplay();
        }
    );

    const release = () => {
        state[stateName] = 0.0;

        updateTouchDisplay();
    };

    button.addEventListener(
        "pointerup",
        release
    );

    button.addEventListener(
        "pointercancel",
        release
    );
}


bindPedal(
    gasButton,
    "throttle"
);

bindPedal(
    brakeButton,
    "brake"
);


/* Fullscreen */

function getFullscreenElement() {
    return (
        document.fullscreenElement
        || document.webkitFullscreenElement
        || null
    );
}


async function toggleFullscreen() {
    try {
        const fullscreenElement =
            getFullscreenElement();

        if (!fullscreenElement) {
            const requestFullscreen =
                touchStage.requestFullscreen
                || touchStage.webkitRequestFullscreen;

            if (requestFullscreen) {
                await requestFullscreen.call(
                    touchStage
                );
            }

            if (
                screen.orientation
                && screen.orientation.lock
            ) {
                try {
                    await screen.orientation.lock(
                        "landscape"
                    );
                } catch (error) {
                }
            }

        } else {
            const exitFullscreen =
                document.exitFullscreen
                || document.webkitExitFullscreen;

            if (exitFullscreen) {
                await exitFullscreen.call(
                    document
                );
            }
        }

    } catch (error) {
        console.error(
            "Fullscreen nicht verfügbar.",
            error
        );
    }
}


fullscreenButton.addEventListener(
    "click",
    toggleFullscreen
);


function updateFullscreenButton() {
    fullscreenButton.textContent =
        getFullscreenElement()
            ? "⛶ VOLLBILD BEENDEN"
            : "⛶ VOLLBILD";
}


document.addEventListener(
    "fullscreenchange",
    updateFullscreenButton
);

document.addEventListener(
    "webkitfullscreenchange",
    updateFullscreenButton
);


/* Sicherheit */

window.addEventListener(
    "blur",
    resetControls
);


document.addEventListener(
    "visibilitychange",
    () => {
        if (document.hidden) {
            resetControls();
        }
    }
);


window.addEventListener(
    "resize",
    detectControlMode
);


/* Start */

detectControlMode();
updateDisplay();

connectControlWebSocket();
connectTelemetryWebSocket();
connectCameraWebSocket();

setInterval(
    sendState,
    50
);
