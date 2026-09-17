\newpage

# Dokumentation
\textauthor{Chloe Pripfl}

Die Projektdokumentation beschreibt den tatsächlichen Stand der praktischen Umsetzung der Diplomarbeit. Da es sich um eine nachgebrachte Diplomarbeit handelt, wird auf eine zeitliche Einteilung in Projektphasen oder Berichtszeiträume verzichtet. Stattdessen wird der aktuelle Projektstatus anhand der umgesetzten Funktionen, der aufgetretenen Probleme und der daraus getroffenen technischen Entscheidungen dokumentiert.

## Projektstatus

### Gesamtstatus

* die ursprünglich geplante Umsetzung am physischen IoT-Car konnte aufgrund des fehlenden Zugriffs auf das Fahrzeug nicht durchgeführt werden
* die praktische Umsetzung wurde daher vollständig auf eine digitale Simulation verlagert
* ROS 2 und Gazebo Sim wurden als zentrale Entwicklungs- und Simulationsplattform eingerichtet
* die Entwicklungsumgebung wurde von einer klassischen virtuellen Maschine auf WSL2 verlagert
* ein eigenes digitales Fahrzeugmodell wurde erstellt
* Ackermann-Lenkung und Hinterradantrieb wurden umgesetzt
* eine eigene Teststrecke in Gazebo wurde erstellt
* eine Frontkamera wurde in das Fahrzeugmodell integriert
* ein frontseitiger Abstandssensor wurde umgesetzt
* die Fahrzeuggeschwindigkeit wird aus den Hinterraddrehzahlen berechnet
* eine zentrale Steuerungslogik für Gas, Bremse, Lenkung und Not-Stopp wurde entwickelt
* eine Desktop-Steuerung über Tastatur wurde umgesetzt
* eine Touch-Steuerung für Smartphones wurde erstellt
* Kamerabild, Geschwindigkeit und Abstand werden in der Weboberfläche dargestellt
* die Kommunikation zwischen Browser und ROS 2 erfolgt über einen eigenen Webserver und WebSockets
* der Zugriff auf die Weboberfläche aus dem lokalen Netzwerk wurde eingerichtet
* das Gesamtsystem wurde in Docker übertragen
* die Simulation kann vollständig innerhalb eines Containers gestartet werden
* GPU-Unterstützung für Kamera und Rendering wurde innerhalb von Docker erfolgreich getestet

| Dimension | Status | Maßnahmen |
|:--------------------|:------------------|:-----------------------|
| Leistungsziele | weitgehend erreicht | Simulation, Steuerung, Sensorik, Weboberfläche und Docker-Umgebung wurden umgesetzt |
| Technischer Stand | funktionsfähig und stabil | auftretende Probleme bei Fahrzeugphysik, Sensorik, Netzwerk und Kamerastream wurden schrittweise behoben |
| Kosten | keine relevanten zusätzlichen Kosten | vorhandene Hardware sowie frei verfügbare Software wurden verwendet |
| Dokumentation | in Abschlussphase | technische Umsetzung und Projektergebnisse werden abschließend verschriftlicht |

: Aktueller Projektstatus

### Technische Umsetzung

#### Entwicklungsumgebung

Die ersten Versuche wurden in einer Ubuntu-VM durchgeführt. Dabei zeigte sich, dass die grafische Simulation nur eingeschränkt performant war. Aus diesem Grund wurde die Entwicklungsumgebung auf WSL2 unter Windows verlagert. Dadurch konnte die vorhandene Hardware, insbesondere die NVIDIA-GPU, besser genutzt werden.

ROS 2 übernimmt innerhalb des Projekts die Kommunikation zwischen den einzelnen Komponenten. Gazebo Sim wird für die physikalische Simulation des Fahrzeugs und der Testumgebung eingesetzt.

#### Fahrzeugmodell und Fahrverhalten

Das IoT-Car wurde als eigenes digitales Fahrzeugmodell aufgebaut. Es besteht aus einem Chassis, vier Rädern sowie den benötigten Gelenken für Lenkung und Antrieb.

Für die Lenkung wird ein Ackermann-Steering-Controller verwendet. Die Vorderräder übernehmen die Lenkung, während die Hinterräder angetrieben werden.

Während der Entwicklung zeigte sich, dass das Fahrzeug bei höheren Geschwindigkeiten zunächst nur sehr flache Kurven fahren konnte. Ursache dafür war eine zu hohe Dämpfung der Radgelenke. Durch die Reduktion der Gelenkdämpfung konnte das Fahrverhalten deutlich verbessert werden.

Die maximale Vorwärtsgeschwindigkeit liegt bei ungefähr 10 km/h. Die Rückwärtsgeschwindigkeit wurde geringer gewählt.

#### Testumgebung

Für die Simulation wurde eine eigene Teststrecke erstellt. Diese enthält eine ebene Fahrfläche, Begrenzungswände, Hindernisse, Slalom-Elemente sowie eine Start- beziehungsweise Ziellinie.

Dadurch können Steuerung und Sensorik unter reproduzierbaren Bedingungen getestet werden.

#### Steuerungslogik

Die zentrale Steuerungslogik wurde in einem eigenen ROS-2-Node umgesetzt. Dieser verarbeitet Eingaben für Lenkung, Gas, Bremse und Not-Stopp.

Die Eingaben werden in Fahrbefehle umgewandelt und an den Ackermann-Steering-Controller weitergegeben. Der maximal mögliche Lenkwinkel wird abhängig von der Fahrzeuggeschwindigkeit angepasst.

Zusätzlich wurden Begrenzungen für Beschleunigung, Bremsverzögerung und Lenkgeschwindigkeit umgesetzt, damit das Fahrzeug kontrollierter auf Eingaben reagiert.

Für Entwicklungszwecke wurde außerdem eine Tastatursteuerung erstellt, mit der das Fahrverhalten unabhängig von der Weboberfläche getestet werden konnte.

#### Abstandssensor

An der Fahrzeugfront wurde ein simulierter Abstandssensor integriert. Technisch wird dafür ein LiDAR-Sensor mit einem sehr kleinen horizontalen Messbereich verwendet.

Die Rohdaten werden über ROS 2 bereitgestellt und durch einen eigenen Node ausgewertet. Aus den gültigen Messwerten wird der kleinste Abstand bestimmt. Der maximale Messbereich beträgt 4 Meter.

Beim direkten Kontakt mit einer Wand konnten zunächst unrealistische Sprünge im Messwert auftreten. Die Auswertung wurde deshalb angepasst, damit dieser Sonderfall korrekt behandelt wird.

#### Frontkamera

Die Frontkamera erzeugt kontinuierlich Bilddaten und stellt diese über ROS 2 zur Verfügung.

Während der ersten Tests lag die Kamera zu tief beziehungsweise zu weit innerhalb des Fahrzeugmodells. Dadurch waren Teile des Fahrzeugs im Kamerabild sichtbar. Die Kameraposition wurde deshalb nach oben und vorne versetzt.

#### Geschwindigkeitssensor

Die Fahrzeuggeschwindigkeit wird aus den Winkelgeschwindigkeiten der angetriebenen Hinterräder berechnet.

Aus der mittleren Raddrehzahl und dem bekannten Radradius wird die lineare Geschwindigkeit bestimmt. Zusätzlich wird der Wert in Kilometer pro Stunde umgerechnet und für die Weboberfläche bereitgestellt.

Bei der ersten Umsetzung war das Vorzeichen der Geschwindigkeit vertauscht. Dieser Fehler wurde anschließend korrigiert.

#### Weboberfläche

Für die externe Bedienung wurde eine webbasierte Benutzeroberfläche entwickelt. Dadurch kann die Simulation ohne zusätzliche Anwendung direkt über einen Webbrowser gesteuert werden.

Am Desktop erfolgt die Steuerung über die Tastatur. Für Smartphones wurde eine eigene Touch-Oberfläche mit Lenkung, Gas, Bremse und Vollbildmodus erstellt.

Zusätzlich werden das Kamerabild, die aktuelle Geschwindigkeit und der Abstand zum nächsten Hindernis dargestellt.

#### Kommunikation zwischen Browser und ROS 2

Für die Verbindung zwischen Browser und ROS 2 wurde ein eigener Webserver entwickelt.

Steuerbefehle werden über WebSockets vom Browser an den Webserver übertragen. Dieser wandelt die Eingaben in ROS-2-Nachrichten um.

Auch Geschwindigkeit und Abstand werden über WebSockets an den Browser übertragen.

Für das Kamerabild wurde zunächst eine MJPEG-Übertragung getestet. Da diese nicht ausreichend flüssig war, wurde der Kamerastream später ebenfalls auf eine WebSocket-basierte Übertragung umgestellt.

#### Netzwerkzugriff

Da die Simulation innerhalb von WSL2 ausgeführt wird, musste der Zugriff aus dem Windows-Netzwerk und von mobilen Endgeräten zusätzlich eingerichtet werden.

Ein gespiegelter Netzwerkmodus führte zu Problemen mit der ROS-2-Kommunikation und der DDS-Erkennung. Deshalb wurde WSL2 weiterhin im NAT-Modus betrieben.

Der benötigte Webserver-Port wurde entsprechend weitergeleitet. Zusätzlich wurde eine Informationsseite mit Verbindungsadresse und QR-Code erstellt.

#### Dockerisierung

Nach der erfolgreichen Umsetzung der Simulation wurde das gesamte System in Docker übertragen.

Dafür wurden ein Dockerfile, eine Compose-Konfiguration und ein Entrypoint erstellt. Beim Start des Containers werden die Gazebo-Simulation, ROS-2-Komponenten, Sensorverarbeitung, Steuerungslogik und der Webserver gemeinsam gestartet.

Gazebo läuft innerhalb des Containers ohne grafische Benutzeroberfläche. Die GPU wird weiterhin für Kamera und Rendering verwendet.

Dadurch kann das Projekt weitgehend unabhängig von einer lokal installierten ROS-2- und Gazebo-Umgebung ausgeführt werden.

### Notwendige Entscheidungen

* Verlagerung der praktischen Umsetzung vom physischen IoT-Car auf eine vollständige Simulation
* Wechsel von einer klassischen virtuellen Maschine auf WSL2
* Verwendung von ROS 2 als Kommunikations- und Steuerungsplattform
* Verwendung von Gazebo Sim als Simulationsumgebung
* Einsatz eines Ackermann-Steering-Controllers für das Fahrzeug
* Reduktion der Gelenkdämpfung zur Verbesserung des Fahrverhaltens
* Umsetzung des Abstandssensors über einen schmalen LiDAR-Messbereich
* Berechnung der Geschwindigkeit aus den angetriebenen Hinterrädern
* Verwendung von WebSockets für Steuerung, Telemetrie und Kamerastream
* Betrieb von WSL2 im NAT-Modus aufgrund von Problemen mit ROS-2-Discovery im gespiegelten Netzwerkmodus
* Dockerisierung des Gesamtsystems zur vereinfachten und reproduzierbaren Ausführung

### Nächste Schritte

* abschließende Dokumentation fertigstellen
* Quellcode und Docker-Image bereitstellen
* abschließende Funktionsprüfung der Simulation durchführen
* Erweiterungsmöglichkeiten im Zukunftsausblick beschreiben
* mögliche spätere Übertragung der entwickelten Steuerungs- und Kommunikationsstruktur auf das physische IoT-Car dokumentieren
