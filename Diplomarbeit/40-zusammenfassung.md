# Zusammenfassung

Im Rahmen dieser Diplomarbeit wurde ein IoT-Car als vernetztes System untersucht und praktisch umgesetzt. Ursprünglich war vorgesehen, ein bereits vorhandenes physisches Fahrzeug direkt weiterzuentwickeln. Da während des notwendigen Entwicklungszeitraums kein durchgehender Zugriff auf das IoT-Car möglich war, wurde die praktische Umsetzung auf eine digitale Simulation verlagert.

Als Grundlage der Simulation wurden ROS 2 und Gazebo Sim eingesetzt. Das Fahrzeug wurde als eigenes digitales Modell aufgebaut und mit einer Ackermann-Lenkung sowie Hinterradantrieb ausgestattet. Zusätzlich wurden eine Frontkamera, ein frontseitiger Abstandssensor und eine Geschwindigkeitsauswertung integriert.

Die Steuerung des Fahrzeugs erfolgt über eine eigene ROS-2-basierte Steuerungslogik. Neben der eigentlichen Fahrzeugbewegung wurden dabei auch Beschleunigung, Bremsverhalten, Lenkung und ein Not-Stopp berücksichtigt.

Ein weiterer Schwerpunkt der Arbeit lag auf der externen Bedienung. Dafür wurde eine webbasierte Benutzeroberfläche entwickelt, die sowohl auf Desktop-PCs als auch auf Smartphones verwendet werden kann. Über diese Oberfläche lässt sich das Fahrzeug steuern, während gleichzeitig das Kamerabild, die aktuelle Geschwindigkeit und der Abstand zum nächsten Hindernis dargestellt werden.

Die Kommunikation zwischen Browser und ROS 2 erfolgt über einen eigenen Webserver und WebSockets. Dadurch können Steuerbefehle sowie Telemetrie- und Kameradaten zwischen der Simulation und dem Endgerät übertragen werden.

Während der Entwicklung traten mehrere technische Herausforderungen auf. Dazu gehörten unter anderem die zunächst unzureichende Simulationsperformance in einer virtuellen Maschine, Probleme mit dem Fahrverhalten des Fahrzeugmodells, die Positionierung und Auswertung der Sensoren sowie die Netzwerkkommunikation zwischen Windows, WSL2, Docker und mobilen Endgeräten.

Durch den Wechsel auf WSL2, Anpassungen an der Fahrzeugphysik, Änderungen an der Sensorverarbeitung sowie die Umstellung des Kamerastreams auf eine WebSocket-basierte Übertragung konnten diese Probleme schrittweise gelöst werden.

Abschließend wurde das gesamte System in eine Docker-Umgebung übertragen. Dadurch können ROS 2, Gazebo, die Steuerungslogik, Sensorverarbeitung und der Webserver gemeinsam in einer definierten Laufzeitumgebung gestartet werden. Dies verbessert die Reproduzierbarkeit und erleichtert die spätere Weiterverwendung des Projekts.

Das Ergebnis der Arbeit ist eine funktionsfähige und modular aufgebaute Simulationsplattform, welche die wesentlichen Funktionen des ursprünglich geplanten IoT-Cars abbildet. Fahrzeugsteuerung, Sensorik, Kommunikation und externe Bedienung konnten erfolgreich miteinander verbunden werden.

Ein möglicher nächster Schritt besteht darin, die entwickelte Steuerungs- und Kommunikationsstruktur auf das reale IoT-Car zu übertragen. Eine zukünftige Diplomarbeit könnte die bestehende Weboberfläche und die bereits entwickelte ROS-2-Struktur aufgreifen und mit der physischen Hardware des Fahrzeugs verbinden. Dadurch könnte die in dieser Arbeit entwickelte Simulation als Grundlage für eine reale Umsetzung dienen.
