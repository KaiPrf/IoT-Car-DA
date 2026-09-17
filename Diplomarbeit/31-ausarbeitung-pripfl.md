# Teilaufgabe Schüler Pripfl

\textauthor{Chloe Pripfl}


## Einleitung

Im Rahmen dieser Teilaufgabe wird das vorhandene Konzept eines IoT-Cars als digitale Simulation umgesetzt. Ziel ist es, die wesentlichen Funktionen eines vernetzten Fahrzeugs unabhängig von der physischen Hardware nachvollziehbar abzubilden. Dazu gehören insbesondere die Fahrzeugbewegung, die Erfassung von Sensordaten, die Bereitstellung eines Kamerabildes sowie die Steuerung über ein externes Endgerät.

Die Simulation soll dabei nicht nur als vereinfachte Darstellung des realen Fahrzeugs dienen, sondern als eigenständig nutzbare Entwicklungs- und Testumgebung. Durch die Trennung der einzelnen Funktionen in mehrere ROS-2-Nodes können Sensorik, Steuerung und Benutzeroberfläche unabhängig voneinander entwickelt und getestet werden. Die Kommunikation zwischen den Komponenten erfolgt über standardisierte ROS-2-Schnittstellen.

Für die Umsetzung werden ROS 2, Gazebo Sim und ros2_control verwendet. Das Fahrzeug wird als URDF-/Xacro-Modell beschrieben und in einer Gazebo-Welt simuliert. Eine virtuelle Frontkamera sowie ein Abstandssensor bilden die für das Projekt relevanten Sensordaten nach. Zusätzlich wird eine browserbasierte Benutzeroberfläche entwickelt, über die das Fahrzeug sowohl am PC als auch über ein Smartphone gesteuert werden kann.

Die fertige Anwendung wird abschließend containerisiert. Dadurch können die für die Simulation benötigten Softwarekomponenten gemeinsam bereitgestellt und auf einem kompatiblen System reproduzierbar gestartet werden.

Die wesentlichen Ziele dieser Teilaufgabe sind damit:

* Erstellung eines simulierten IoT-Cars in Gazebo Sim
* Modellierung einer Ackermann-Lenkung mit angetriebener Hinterachse
* Simulation einer Frontkamera und eines Abstandssensors
* Ermittlung und Bereitstellung der simulierten Fahrzeuggeschwindigkeit
* Steuerung des Fahrzeugs über ROS 2
* Entwicklung einer Weboberfläche für PC und Smartphone
* Übertragung von Kamerabild und Telemetriedaten an den Browser
* Containerisierung der vollständigen Simulationsumgebung


## Theorieteil

### ROS 2

#### Grundprinzip

ROS 2, ausgeschrieben Robot Operating System 2, ist ein Open-Source-Framework für die Entwicklung verteilter Robotiksysteme. Es stellt unter anderem Kommunikationsmechanismen, Bibliotheken, Werkzeuge und standardisierte Schnittstellen bereit. Dadurch können komplexe Systeme in kleinere Softwarekomponenten aufgeteilt werden, die jeweils eine klar definierte Aufgabe übernehmen. [@doi:10.1126/scirobotics.abm6074]

Eine zentrale Einheit innerhalb von ROS 2 ist der sogenannte **Node**. Ein Node ist eine ausführbare Softwarekomponente, die beispielsweise Sensordaten verarbeitet, Steuerbefehle erzeugt oder Zustandsinformationen bereitstellt. Mehrere Nodes bilden gemeinsam den sogenannten ROS Graph und können untereinander Informationen austauschen. [@ROS2Nodes]

Diese Aufteilung ist für das IoT-Car besonders geeignet, da die einzelnen Aufgaben voneinander getrennt umgesetzt werden können. Beispielsweise sind die Fahrzeugsteuerung, die Geschwindigkeitsberechnung, die Abstandsmessung und der Webserver als eigenständige Komponenten realisiert. Änderungen an einer Komponente erfordern dadurch nicht automatisch eine Änderung des gesamten Systems.

ROS 2 unterstützt außerdem die Zusammenfassung mehrerer Nodes innerhalb eines gemeinsamen Prozesses. Diese sogenannte Node Composition kann den Kommunikationsaufwand innerhalb größerer Robotiksysteme reduzieren und erlaubt eine flexiblere Strukturierung der Anwendung. [@doi:10.48550/arXiv.2305.09933]


#### Kommunikation zwischen Nodes

Die Kommunikation in ROS 2 erfolgt hauptsächlich über **Topics**, **Services** und **Actions**. Für kontinuierliche Datenströme wie Sensordaten, Kamerainformationen oder Steuerbefehle werden überwiegend Topics verwendet. Ein Node veröffentlicht dabei Nachrichten auf einem Topic, während andere Nodes dieses Topic abonnieren können.

Die übertragenen Nachrichten besitzen definierte Datentypen. ROS 2 stellt dafür zahlreiche Standardtypen zur Verfügung und ermöglicht zusätzlich die Definition eigener Message- und Service-Schnittstellen. [@ROS2Interfaces]

Für die eigentliche Kommunikation verwendet ROS 2 eine Middleware-Schicht. Über die sogenannte RMW-Schnittstelle können unterschiedliche DDS-basierte Middleware-Implementierungen verwendet werden. Dadurch ist die Kommunikation nicht fest an eine einzelne Transportimplementierung gebunden. [@ROS2Middleware]

Im Gegensatz zu ROS 1 ist für die grundlegende Discovery zwischen den Teilnehmern kein zentraler ROS-Master erforderlich. Die beteiligten Nodes können sich innerhalb einer ROS-2-Domain gegenseitig finden. Über die Umgebungsvariable `ROS_DOMAIN_ID` können mehrere voneinander getrennte ROS-2-Netzwerke auf demselben physischen Netzwerk betrieben werden. [@ROS2Environment]

Für die Simulation werden unter anderem folgende Topics verwendet:

| Topic | Inhalt |
|:------|:-------|
| `/cmd_vel` | Geschwindigkeits- und Lenkvorgaben für das Fahrzeug |
| `/car/camera/image` | Bilddaten der simulierten Frontkamera |
| `/car/camera/camera_info` | Kameraparameter der simulierten Kamera |
| `/car/front_scan` | Messwerte des simulierten Distanzsensors |
| `/car/distance` | Aufbereiteter Abstand zum nächsten Hindernis |
| `/car/distance_valid` | Gültigkeitsstatus der Abstandsmessung |
| `/car/speed` | Berechnete Geschwindigkeit in m/s |
| `/car/speed_kmh` | Berechnete Geschwindigkeit in km/h |
| `/control/input` | Eingaben der Benutzeroberfläche für Lenkung, Gas und Bremse |


### URDF und Xacro

Damit ROS 2 und Gazebo den Aufbau eines Roboters oder Fahrzeugs kennen, wird dessen Struktur in einem Robotermodell beschrieben. Ein URDF-Modell definiert dazu einzelne **Links** und **Joints**. Links beschreiben starre Körper, während Joints die Beziehungen und Bewegungsmöglichkeiten zwischen diesen Körpern festlegen.

Das Paket `robot_state_publisher` verwendet eine solche Roboterbeschreibung, um die räumlichen Beziehungen der einzelnen Komponenten innerhalb des ROS-Systems bereitzustellen. [@RobotStatePublisher]

Bei umfangreicheren Modellen kann eine einzige URDF-Datei schnell unübersichtlich werden. Deshalb wird im Projekt **Xacro** verwendet. Xacro erweitert XML um Makros, Variablen und Includes und ermöglicht dadurch eine modulare Aufteilung des Robotermodells. [@Xacro]

Das Fahrzeugmodell wird im Projekt deshalb auf mehrere Dateien verteilt. Das grundlegende Fahrzeug befindet sich in `vehicle_v2.urdf.xacro`. Kamera und Abstandssensor werden über zusätzliche Xacro-Dateien eingebunden. Dadurch können einzelne Komponenten unabhängig verändert werden, ohne die gesamte Fahrzeugbeschreibung bearbeiten zu müssen.


### Gazebo Sim

Gazebo Sim ist eine Simulationsumgebung für Robotik und autonome Systeme. Sie ermöglicht die Simulation von Robotermodellen, physikalischen Interaktionen, Sensoren und virtuellen Umgebungen. Neben der grafischen Darstellung kann Gazebo auch ohne sichtbare Benutzeroberfläche betrieben werden, was insbesondere für automatisierte oder containerisierte Anwendungen relevant ist. [@GazeboGettingStarted]

Für das IoT-Car übernimmt Gazebo mehrere Aufgaben gleichzeitig. Das Programm simuliert die Fahrzeugphysik, verarbeitet die Rad- und Lenkbewegungen, berechnet Kollisionen und erzeugt die virtuellen Sensordaten. Zusätzlich wird eine eigene Testumgebung verwendet, in der das Fahrzeug gesteuert und die Sensorik überprüft werden kann.


#### Simulierte Sensoren

Gazebo stellt unterschiedliche Sensortypen zur Verfügung und kann deren Messwerte während der Simulation erzeugen. Dazu zählen unter anderem Kameras, LiDAR-Sensoren, IMUs und weitere Sensorarten. [@GazeboSensors]

Im IoT-Car werden zwei Sensoren verwendet. Eine virtuelle Kamera erzeugt ein Frontbild des Fahrzeugs. Zusätzlich wird ein nach vorne gerichteter Distanzsensor verwendet, der auf einem simulierten GPU-LiDAR basiert. Die Sensorkonfiguration wird direkt innerhalb der Fahrzeugbeschreibung vorgenommen. [@GazeboSensorTutorial]

Die Kamera liefert ein Bild mit einer Auflösung von 640 × 360 Pixeln und einer Aktualisierungsrate von 30 Hz. Die Bilddaten werden auf dem Topic `/car/camera/image` bereitgestellt. Der Distanzsensor arbeitet mit einer maximalen Messdistanz von 4 m und veröffentlicht seine Rohdaten auf `/car/front_scan`.


### Verbindung zwischen Gazebo und ROS 2

Gazebo verwendet intern eigene Transportmechanismen. Damit die simulierten Daten innerhalb von ROS 2 zur Verfügung stehen, wird die `ros_gz_bridge` eingesetzt. Sie übersetzt Nachrichten zwischen Gazebo Transport und ROS 2 und ermöglicht beispielsweise die Weitergabe des Kamerabildes, der Laserscandaten und der Simulationszeit. [@ROSGazeboBridge]

Im Projekt werden unter anderem `/clock`, `/car/camera/image`, `/car/camera/camera_info` und `/car/front_scan` über diese Bridge an ROS 2 weitergegeben.

Für die Steuerung der simulierten Gelenke kommt zusätzlich `gz_ros2_control` zum Einsatz. Dadurch können ros2_control-Controller direkt auf die Gelenke des Gazebo-Modells zugreifen. [@gzros2controlAckermann]


### Ackermann-Lenkung

Bei einem Fahrzeug mit Ackermann-Lenkung werden die beiden gelenkten Vorderräder beim Kurvenfahren nicht exakt um denselben Winkel eingeschlagen. Das kurveninnere Rad benötigt einen größeren Lenkwinkel als das kurvenäußere Rad, da beide Räder unterschiedliche Kurvenradien zurücklegen.

Das simulierte IoT-Car verwendet zwei gelenkte Vorderräder und zwei angetriebene Hinterräder. Die Fahrbefehle werden über einen Ackermann-Steering-Controller auf die entsprechenden Gelenke umgesetzt. Der Controller erhält eine gewünschte Längsgeschwindigkeit und eine Lenkvorgabe und berechnet daraus die notwendigen Gelenkbewegungen.

Für die Fahrdynamik sind insbesondere Radstand, Spurweite und Radradius relevant. Im Modell werden ein Radstand von 0,26 m, eine Spurweite von 0,21 m und ein Radradius von 0,055 m verwendet.


### Browserbasierte Steuerung

Die Benutzeroberfläche wird als Webanwendung umgesetzt. Dadurch ist keine eigene Smartphone-App notwendig. Ein Gerät im selben Netzwerk benötigt lediglich einen aktuellen Webbrowser. Die Steuerbefehle werden von der Weboberfläche an den Webserver übertragen und von dort als ROS-2-Nachrichten in das System eingespeist.

Neben der Steuerung werden auch Telemetriedaten im Browser dargestellt. Dazu gehören die aktuelle Geschwindigkeit und die gemessene Distanz zum nächsten Hindernis. Zusätzlich wird das Bild der simulierten Frontkamera übertragen.

Die Steueroberfläche unterscheidet zwischen Desktop- und Touch-Bedienung. Am PC kann das Fahrzeug über die Tastatur gesteuert werden. Auf einem Smartphone werden ein virtueller Lenkbereich sowie getrennte Gas- und Bremstasten angezeigt. Dadurch kann dieselbe Anwendung ohne separate Installation auf unterschiedlichen Endgeräten verwendet werden.


### Containerisierung

Für die spätere Weitergabe und reproduzierbare Ausführung wird die Simulationsumgebung als Docker-Container bereitgestellt. Im Docker-Image befinden sich die benötigte ROS-2-Umgebung, die Projektquellen und die notwendigen Softwareabhängigkeiten.

Die Simulation wird innerhalb des Containers ohne Gazebo-GUI gestartet. Die Sensordaten werden dennoch berechnet und können über die Weboberfläche betrachtet werden. Der Webserver wird über Port 8080 bereitgestellt. Dadurch bleibt die eigentliche Simulation innerhalb des Containers gekapselt, während die Bedienung über einen normalen Browser erfolgt.

Die Containerisierung reduziert die Anzahl manueller Installationsschritte auf einem Zielsystem. Statt ROS 2, Gazebo und die einzelnen Python-Abhängigkeiten separat einzurichten, kann das vorbereitete Image gestartet werden, sofern Docker und die erforderliche GPU-Unterstützung auf dem System vorhanden sind.


## Praxisteil

### Entwicklungsumgebung

Die Entwicklung der Simulation erfolgt unter Windows mit WSL2. Innerhalb von WSL wird Ubuntu 26.04 eingesetzt. Als ROS-2-Version kommt ROS 2 Lyrical zum Einsatz. Die Simulation selbst wird mit Gazebo Sim ausgeführt.

Für die grafische Beschleunigung kann die in WSL verfügbare GPU-Schnittstelle verwendet werden. Auf dem Entwicklungssystem steht dafür eine NVIDIA GeForce RTX 5070 Laptop GPU zur Verfügung. Für die spätere Container-Version wurde zusätzlich die GPU-Nutzung innerhalb von Docker Desktop getestet.

Der ROS-2-Workspace befindet sich unter:

```text
~/iot_car_ws
```

Das zentrale ROS-2-Paket trägt den Namen:

```text
iot_car_description
```

Die wichtigsten Projektbereiche sind dabei wie folgt strukturiert:

```text
iot_car_ws/
|-- Dockerfile
|-- compose.yaml
|-- docker/
|-- src/
|   `-- iot_car_description/
|       |-- config/
|       |-- launch/
|       |-- scripts/
|       |-- urdf/
|       |-- web/
|       |-- worlds/
|       |-- CMakeLists.txt
|       `-- package.xml
`-- tools/
```

Die Unterteilung trennt Robotermodell, Konfiguration, Python-Nodes, Weboberfläche, Simulationswelten und Startdateien voneinander.


### Aufbau des Fahrzeugmodells

Das Fahrzeug wird in der Datei `vehicle_v2.urdf.xacro` beschrieben. Die Karosserie bildet den zentralen `base_link`. Daran sind vier Räder sowie die Sensoren befestigt.

Die Hinterräder werden angetrieben. Die Vorderräder besitzen jeweils ein zusätzliches Lenk-Gelenk und können frei rollen. Für die Steuerung werden folgende Gelenke verwendet:

```text
left_wheel_steering_joint
right_wheel_steering_joint
rear_left_wheel_joint
rear_right_wheel_joint
```

Die Trennung zwischen Lenkung und Antrieb entspricht damit dem Aufbau eines klassischen Fahrzeugs mit gelenkter Vorderachse und angetriebener Hinterachse.

Während der Entwicklung zeigte sich, dass eine zu hohe Dämpfung an den Radgelenken einen erheblichen Einfluss auf das Fahrverhalten hatte. Bei einem Dämpfungswert von `0.05` entstand ein hoher künstlicher Widerstand. Das Fahrzeug konnte dadurch bei höheren Geschwindigkeiten Kurven nur unzureichend fahren und die Räder zeigten ein deutliches Schlupfverhalten. Nach der Reduktion des Dämpfungswerts auf `0.001` verhielt sich das Fahrzeug wesentlich stabiler und die berechneten Lenkbewegungen konnten korrekt umgesetzt werden.


### ros2_control und Fahrzeugcontroller

Die Konfiguration des Fahrzeugcontrollers befindet sich in `vehicle_v2_controllers.yaml`. Der Controller arbeitet mit folgenden geometrischen Grundwerten:

| Parameter | Wert |
|:----------|----:|
| Radstand | 0,26 m |
| Spurweite | 0,21 m |
| Radradius | 0,055 m |
| Controller-Aktualisierungsrate | 100 Hz |

Zusätzlich wird ein `joint_state_broadcaster` verwendet. Dieser stellt die aktuellen Gelenkzustände innerhalb von ROS 2 zur Verfügung.

Die beiden Hinterräder werden als `traction_joints_names` und die beiden Lenkgelenke der Vorderachse als `steering_joints_names` an den Ackermann-Controller übergeben. Die Odometrie wird vom Controller veröffentlicht und die Transformation zwischen `odom` und `base_link` bereitgestellt.


### Entwicklung der Fahrsteuerung

Die eigentliche Eingabelogik wird im Node `game_control.py` umgesetzt. Der Node empfängt Steuerwerte über das Topic `/control/input`. Als Nachrichtentyp wird `sensor_msgs/Joy` verwendet.

Die Eingaben sind folgendermaßen aufgebaut:

```text
axes[0]   Lenkung
axes[1]   Gas
axes[2]   Bremse
buttons[0] Not-Aus
```

Der Node verarbeitet diese Werte und erzeugt daraus `TwistStamped`-Nachrichten für `/cmd_vel`. Die Steuerung arbeitet mit einer Aktualisierungsrate von 50 Hz.

Für das Fahrzeug wurden eine maximale Vorwärtsgeschwindigkeit von ungefähr 2,78 m/s und eine maximale Rückwärtsgeschwindigkeit von ungefähr 1,39 m/s festgelegt. Dies entspricht etwa 10 km/h vorwärts und 5 km/h rückwärts.

Damit sich das Fahrzeug bei unterschiedlichen Geschwindigkeiten kontrollierbar verhält, ist der maximale Lenkwinkel geschwindigkeitsabhängig. Bei niedriger Geschwindigkeit ist ein größerer Lenkeinschlag zulässig. Mit steigender Geschwindigkeit wird dieser reduziert. Zusätzlich werden Beschleunigung, Verzögerung und das selbstständige Zurückstellen der Lenkung begrenzt. Dadurch entstehen weichere Übergänge und ein besser kontrollierbares Fahrverhalten.

Ein Input-Timeout sorgt dafür, dass bei ausbleibenden Steuerbefehlen nicht dauerhaft der zuletzt empfangene Fahrbefehl ausgeführt wird.


### Teststrecke

Für die Funktionsprüfung wurde eine eigene Gazebo-Welt mit dem Namen `test_track_v2.sdf` erstellt. Die Testumgebung enthält eine abgegrenzte Fahrfläche, mehrere Wände, Hindernisse und Slalom-Elemente.

Die Strecke erfüllt mehrere Aufgaben. Gerade Abschnitte dienen zur Überprüfung der Beschleunigung und Geschwindigkeitsmessung. Kurven und Slalom-Elemente ermöglichen die Kontrolle der Lenkung. Wände werden verwendet, um den Abstandssensor sowie das Kollisionsverhalten des Fahrzeugmodells zu testen.

Die Simulationsphysik arbeitet mit einer Schrittweite von 0,001 s. Dadurch kann die Fahrzeugbewegung mit ausreichend hoher zeitlicher Auflösung berechnet werden.


### Frontkamera

Die Frontkamera ist als Gazebo-Kamerasensor am Fahrzeug befestigt. Sie erzeugt RGB-Bilddaten mit einer Auflösung von 640 × 360 Pixeln und einer Aktualisierungsrate von 30 Hz.

Die Bilddaten werden über die Gazebo-ROS-Bridge auf `/car/camera/image` veröffentlicht. Zusätzlich stehen auf `/car/camera/camera_info` die zugehörigen Kamerainformationen zur Verfügung.

Während der Entwicklung musste die Position der Kamera mehrfach angepasst werden. Befand sich die Kamera zu tief oder zu weit innerhalb der Fahrzeuggeometrie, waren Teile des Fahrzeugs im Bild sichtbar oder die Perspektive schnitt durch das Modell. Durch die Verlagerung der Kamera nach vorne und oben wurde eine besser nutzbare Frontansicht erreicht.


### Abstandssensor

Für die Abstandsmessung wird ein schmaler GPU-LiDAR-Sensor verwendet. Dieser befindet sich an der Fahrzeugfront und ist nach vorne ausgerichtet. Der Sensor besitzt eine maximale Reichweite von 4 m und arbeitet mit 20 Hz.

Die Rohdaten werden als `LaserScan` auf `/car/front_scan` veröffentlicht. Der selbst entwickelte Node `front_distance_sensor.py` verarbeitet diese Daten weiter. Aus allen gültigen Messwerten wird der kleinste Abstand bestimmt und anschließend als `Float32` auf `/car/distance` veröffentlicht.

Zusätzlich wird auf `/car/distance_valid` ein Bool-Wert bereitgestellt. Dieser gibt an, ob die aktuelle Messung als gültig betrachtet wird.

Bei ersten Tests trat beim direkten Kontakt mit einer Wand ein unerwünschter Sprung des Messwertes auf. Sobald sich die simulierte Sensorgeometrie sehr nahe an oder teilweise innerhalb der Kollisionsgeometrie befand, konnte der Sensor plötzlich wieder einen großen Abstand liefern. Dieses Verhalten wurde in der Auswertung abgefangen. Befand sich das Fahrzeug unmittelbar zuvor praktisch an einem Hindernis und sprang der Messwert unplausibel stark nach oben, wird weiterhin ein Abstand von 0 m ausgegeben.


### Geschwindigkeitsmessung

Die Geschwindigkeit wird im Node `speed_sensor.py` aus den Winkelgeschwindigkeiten der beiden angetriebenen Hinterräder berechnet. Dazu wird zunächst der Mittelwert der beiden Gelenkgeschwindigkeiten gebildet und anschließend mit dem bekannten Radradius multipliziert.

Vereinfacht gilt:

$$
v = \omega \cdot r
$$

Dabei ist $v$ die lineare Geschwindigkeit, $\omega$ die Winkelgeschwindigkeit des Rades und $r$ der Radradius.

Das Ergebnis wird sowohl in Metern pro Sekunde auf `/car/speed` als auch in Kilometern pro Stunde auf `/car/speed_kmh` veröffentlicht.

Während der Implementierung war die Vorzeichenrichtung zunächst invertiert. Dadurch wurde eine Vorwärtsfahrt als negative Geschwindigkeit und die Rückwärtsfahrt als positive Geschwindigkeit dargestellt. Nach Anpassung der Berechnung entspricht das Vorzeichen nun der tatsächlichen Fahrtrichtung.


### Webserver

Die Verbindung zwischen ROS 2 und dem Browser wird durch `web_server.py` hergestellt. Der Webserver basiert auf `aiohttp` und wird auf Port 8080 bereitgestellt.

Der Server übernimmt mehrere Aufgaben gleichzeitig:

* Bereitstellung der HTML-, CSS- und JavaScript-Dateien
* Empfang der Benutzereingaben über WebSocket
* Veröffentlichung der Eingaben auf `/control/input`
* Übertragung der aktuellen Telemetriedaten an den Browser
* Konvertierung und Übertragung der Kamerabilder
* Bereitstellung einer Informationsseite mit Verbindungsdaten und QR-Code

Die WebSocket-Verbindung für die Steuerung überträgt die aktuellen Eingaben mit bis zu 50 Hz an den ROS-2-Teil der Anwendung. Geschwindigkeit und Distanz werden mit geringerer Rate an die Benutzeroberfläche übertragen.

Für den Kamerastream wird das ROS-Bild über `cv_bridge` und OpenCV verarbeitet und als JPEG komprimiert. Anschließend wird jeweils nur das aktuellste verfügbare Bild an den Browser übertragen. Ältere Bilder werden nicht in einer langen Warteschlange gespeichert. Dadurch wird verhindert, dass sich bei langsamer Netzwerkübertragung eine immer größere Verzögerung aufbaut.


### Desktop-Steuerung

Auf einem Desktop-PC kann die Steuerungsseite mit Tastatur und Maus verwendet werden. Die Fahrtrichtung wird über die WASD-Tasten gesteuert. Zusätzlich kann über die Leertaste ein Not-Stopp ausgelöst werden.

Neben dem Kamerabild werden Geschwindigkeit und Abstand eingeblendet. Dadurch stehen die wichtigsten Zustandsinformationen des simulierten Fahrzeugs direkt in derselben Oberfläche zur Verfügung.


### Smartphone-Steuerung

Für Smartphones wird dieselbe Webanwendung in einem angepassten Touch-Layout dargestellt. Das Kamerabild dient dabei als großflächiger Hintergrund.

Auf der linken Seite befindet sich die Lenksteuerung. Die Position des Fingers wird in einen normierten Lenkwert zwischen links und rechts umgerechnet. Auf der rechten Seite stehen getrennte Tasten für Gas und Bremse zur Verfügung.

Zusätzlich kann die Anwendung in den Vollbildmodus geschaltet werden. Wenn der verwendete Browser und das Betriebssystem dies unterstützen, wird gleichzeitig versucht, die Bildschirmausrichtung auf Querformat zu setzen.

Da die Steuerung vollständig im Browser ausgeführt wird, muss auf dem Smartphone keine zusätzliche Anwendung installiert werden. Befinden sich Computer und Smartphone im selben Netzwerk und ist Port 8080 erreichbar, kann die Steuerseite direkt über die IP-Adresse des Rechners geöffnet werden.


### Netzwerk unter WSL2

Während der Entwicklung wurde die Netzwerkkommunikation zwischen Windows, WSL2, ROS 2 und mobilen Endgeräten getestet. Für die Simulation erwies sich der NAT-Netzwerkmodus von WSL2 als zuverlässiger als der getestete Mirrored-Modus, da im Mirrored-Modus Probleme bei der ROS-2-DDS-Discovery auftraten.

Für den direkten Betrieb aus WSL2 wurde deshalb eine Portweiterleitung von Windows auf die WSL-Instanz eingerichtet. Dadurch konnte der Webserver unter der Windows-IP-Adresse auf Port 8080 vom Smartphone erreicht werden.

Beim späteren Betrieb über Docker Desktop übernimmt Docker die Veröffentlichung des Ports. Der Container stellt dafür Port 8080 nach außen bereit.


### Dockerisierung

Nachdem die Simulation und die Websteuerung unter WSL2 stabil funktionierten, wurde das Projekt in einen Docker-Container übertragen.

Das `Dockerfile` verwendet ein ROS-2-Basisimage und installiert die benötigten Abhängigkeiten. Dazu gehören unter anderem Gazebo-ROS-Pakete, ros2_control, ros2_controllers, Xacro, OpenCV, `cv_bridge`, `aiohttp` und QR-Code-Unterstützung.

Anschließend wird der Quellcode in das Image kopiert und der Workspace mit `colcon build --symlink-install` gebaut.

Die Datei `compose.yaml` beschreibt den eigentlichen Container. Dort werden unter anderem folgende Einstellungen definiert:

```text
Image:         iot-car-sim:latest
Container:     iot-car-sim
Web-Port:      8080:8080
Shared Memory: 512 MB
GPU:           aktiviert
```

Für die Container-Version wird Gazebo ohne grafische Oberfläche gestartet. Der Aufruf verwendet Headless Rendering, sodass die virtuelle Kamera weiterhin gerendert wird, ohne ein Gazebo-Fenster anzuzeigen.

Die GPU-Durchleitung in Docker wurde separat mit einem NVIDIA-CUDA-Container überprüft. Dadurch konnte sichergestellt werden, dass die NVIDIA-GPU innerhalb von Docker verfügbar ist.

Nach dem Build kann die vollständige Anwendung mit Docker Compose gestartet werden. Der Browserzugriff erfolgt anschließend weiterhin über Port 8080.


### Startablauf der Container-Version

Für die Container-Version wurde ein eigener ROS-2-Launch-Ablauf erstellt. Beim Start werden die benötigten Komponenten automatisch gestartet:

1. Gazebo Sim mit der Testwelt
2. Robotermodell des IoT-Cars
3. ROS-Gazebo-Bridges
4. `joint_state_broadcaster`
5. Ackermann-Steering-Controller
6. `game_control.py`
7. `speed_sensor.py`
8. `front_distance_sensor.py`
9. `web_server.py`

Dadurch muss der Benutzer die einzelnen Nodes nicht manuell in mehreren Terminals starten.


### Aufgetretene Probleme und Lösungen

Während der Entwicklung traten mehrere Probleme auf, die für die endgültige Struktur des Projekts relevant waren.

#### Fahrverhalten und Radwiderstand

Das Fahrzeug konnte anfangs bei höherer Geschwindigkeit kaum enge Kurven fahren. Die Ursache lag nicht ausschließlich in der Ackermann-Berechnung, sondern hauptsächlich in einer zu hohen Gelenkdämpfung der Räder. Durch die Reduktion der Dämpfung von `0.05` auf `0.001` konnte der künstliche Rollwiderstand deutlich reduziert werden.

#### Leistung der Simulation

In der virtuellen Maschine war die Gazebo-Simulation teilweise stark verlangsamt. Der Real-Time-Factor fiel zeitweise deutlich unter 1. Der Wechsel auf WSL2 und die Nutzung der GPU verbesserten die Situation erheblich. In der späteren Konfiguration konnte die Simulation annähernd in Echtzeit betrieben werden.

#### Abstandsmessung bei Wandkontakt

Beim sehr nahen Kontakt mit Wänden entstanden teilweise unplausible Distanzwerte. Neben der Anpassung der Sensorgeometrie wurde deshalb eine Plausibilitätsprüfung im Auswertungs-Node ergänzt.

#### Kamerastream

Eine erste Streaming-Variante war insbesondere auf mobilen Geräten nicht ausreichend flüssig. Durch die Umstellung auf eine WebSocket-basierte Übertragung und das Prinzip, immer nur das aktuellste Kamerabild zu übertragen, konnte die wahrgenommene Verzögerung reduziert werden.

#### Statische Webdateien

Da der ROS-2-Workspace mit `--symlink-install` gebaut wird, liegen Teile der Webressourcen als symbolische Links vor. Der Webserver musste deshalb so konfiguriert werden, dass diese Dateien korrekt ausgeliefert werden können.

#### Netzwerk und ROS-2-Discovery

Der getestete Mirrored-Netzwerkmodus von WSL2 führte zu Problemen mit der ROS-2-Discovery. Deshalb wurde für die Entwicklung wieder auf NAT zurückgewechselt und der Webzugriff gezielt über Portweiterleitung beziehungsweise später über Docker-Port-Publishing gelöst.


### Ergebnis der Teilaufgabe

Als Ergebnis steht eine funktionsfähige digitale Simulation des IoT-Cars zur Verfügung. Das Fahrzeug kann in Gazebo auf einer eigenen Teststrecke gefahren werden. Die Lenkung wird über einen Ackermann-Controller umgesetzt und das Fahrzeug erreicht ungefähr 10 km/h in Vorwärts- sowie 5 km/h in Rückwärtsrichtung.

Die virtuelle Frontkamera stellt kontinuierlich Bilddaten bereit. Der Abstandssensor erkennt Hindernisse vor dem Fahrzeug bis zu einer Entfernung von 4 m. Zusätzlich wird die aktuelle Geschwindigkeit aus den simulierten Radbewegungen berechnet.

Alle für die Bedienung relevanten Daten werden in einer browserbasierten Oberfläche zusammengeführt. Die Anwendung kann am PC oder über ein Smartphone im selben Netzwerk verwendet werden. Damit werden Steuerung, Kamerabild und Telemetrie über ein externes Endgerät zugänglich gemacht, ohne dass dafür eine eigene Client-Anwendung installiert werden muss.

Durch die abschließende Dockerisierung kann die vollständige Simulationsumgebung gemeinsam mit ihren Softwareabhängigkeiten als Image bereitgestellt werden. Dadurch lässt sich der entwickelte Stand einfacher archivieren, weitergeben und auf anderen kompatiblen Systemen erneut starten.


### Grenzen und mögliche Erweiterungen

Die entwickelte Simulation bildet gezielt die für diese Arbeit relevanten Funktionen ab und ist keine vollständige physikalische Nachbildung eines realen Fahrzeugs. Reifenverformung, exakte Fahrwerkskinematik, reale Sensorfehler und weitere mechanische Einflüsse werden nur vereinfacht berücksichtigt.

Die Weboberfläche ist für den Einsatz innerhalb eines lokalen Netzwerks ausgelegt. Für einen produktiven Betrieb über öffentliche Netzwerke wären zusätzliche Sicherheitsmaßnahmen wie Authentifizierung, verschlüsselte Verbindungen und eine differenzierte Rechteverwaltung notwendig.

Die modulare ROS-2-Struktur ermöglicht jedoch mehrere Erweiterungen. Denkbar sind zusätzliche Sensoren, autonome Fahrfunktionen, Hindernisvermeidung, Spurverfolgung oder die spätere Übertragung derselben ROS-2-Schnittstellen auf ein reales IoT-Car. Gerade die Trennung zwischen Fahrzeugsteuerung, Sensorverarbeitung und Benutzeroberfläche erleichtert es, einzelne simulierte Komponenten schrittweise durch reale Hardware zu ersetzen.