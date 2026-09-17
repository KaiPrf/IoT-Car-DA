# Zielsetzung
\textauthor{Chloe Pripfl}

## Motivation der Arbeit

Die Motivation für diese Diplomarbeit ergibt sich aus der zunehmenden Bedeutung vernetzter Systeme und IoT-Technologien in Alltag, Industrie und Ausbildung. Gleichzeitig zeigt sich, dass der Einstieg in diese Themenbereiche durch die Vielzahl an Technologien, Frameworks und Schnittstellen schnell komplex werden kann.

Als Praxisbeispiel dient ein bereits vorhandenes IoT-Car. Ursprünglich war vorgesehen, dieses Fahrzeug direkt weiterzuentwickeln und dessen Sensorik, Steuerung und Kommunikation praktisch umzusetzen. Da das Fahrzeug über den Sommer nicht zur Verfügung gestellt werden konnte, war eine kontinuierliche Entwicklung und Erprobung am realen System jedoch nicht möglich.

Aus diesem Grund wurde die praktische Umsetzung auf eine digitale Simulation verlagert. Dadurch können die wesentlichen Funktionen des geplanten Systems unabhängig von der Verfügbarkeit der physischen Hardware entwickelt und getestet werden.

Die Simulation soll zeigen, wie Fahrzeugsteuerung, Sensorik, Kommunikation und eine externe Benutzeroberfläche zu einem modularen Gesamtsystem verbunden werden können. Ein besonderer Schwerpunkt liegt auf ROS 2 als Kommunikations- und Steuerungsbasis sowie auf Gazebo Sim für die virtuelle Abbildung des Fahrzeugs und seiner Umgebung.

## Ziel der Diplomarbeit

Ziel der Diplomarbeit ist die Konzeption, Umsetzung und Dokumentation einer modularen Simulation eines IoT-Cars. Das Fahrzeug soll in einer virtuellen Umgebung steuerbar sein, Sensordaten bereitstellen und über eine externe Benutzeroberfläche bedient werden können.

Im Rahmen der Arbeit sollen insbesondere folgende Ziele erreicht werden:

- Erstellung eines digitalen Fahrzeugmodells
- Umsetzung von Antrieb und Ackermann-Lenkung
- Integration einer Frontkamera
- Integration eines frontseitigen Abstandssensors
- Erfassung der Fahrzeuggeschwindigkeit
- Kommunikation der einzelnen Komponenten über ROS 2
- Entwicklung einer zentralen Steuerungslogik
- Entwicklung einer webbasierten Kontrolloberfläche
- Steuerung über Desktop-PC und Smartphone
- Übertragung von Kamerabild und Telemetriedaten an die Benutzeroberfläche
- Erstellung einer virtuellen Testumgebung in Gazebo Sim
- Bereitstellung der Simulation in einer Docker-Umgebung
- nachvollziehbare Dokumentation des technischen Aufbaus und der praktischen Umsetzung

Das Gesamtsystem soll modular aufgebaut sein, sodass Fahrzeugmodell, Sensorik, Steuerung und Benutzeroberfläche möglichst unabhängig voneinander angepasst oder erweitert werden können.

## Nicht-Ziele der Diplomarbeit

Die Diplomarbeit verfolgt bewusst nicht das Ziel, ein marktreifes oder industriell zertifiziertes Fahrzeugsteuerungssystem zu entwickeln. Der Schwerpunkt liegt auf einer funktionsfähigen und nachvollziehbaren Simulation.

Nicht Bestandteil der Arbeit sind daher:

- Entwicklung oder Fertigung eigener Fahrzeughardware
- vollständiger Umbau oder Wiederaufbau des vorhandenen physischen IoT-Cars
- Entwicklung eigener Kommunikationsprotokolle
- sicherheitszertifizierte Steuerung für reale Fahrzeuge oder Maschinen
- vollständige autonome Navigation
- komplexe Bildverarbeitung oder Objekterkennung
- Optimierung auf maximale Simulationsleistung
- industrielle Skalierung oder Hochverfügbarkeitsanforderungen
- vollständige Abbildung aller möglichen IoT-Anwendungsfälle

Die entwickelte Lösung dient in erster Linie als technisches Demonstrations- und Lernsystem.

## Veränderung durch diese Arbeit

Durch diese Arbeit wird aus einem ursprünglich hardwarebezogenen IoT-Car-Projekt eine reproduzierbare und modular aufgebaute Simulationsplattform.

Das Fahrzeug, seine Sensorik und die Steuerung können unabhängig von der realen Hardware ausgeführt und getestet werden. Die einzelnen Funktionen werden dabei in mehrere klar getrennte Komponenten aufgeteilt. Dazu gehören das Fahrzeugmodell, die Gazebo-Simulation, ROS-2-Nodes zur Verarbeitung von Steuer- und Sensordaten, die Weboberfläche sowie die Docker-Umgebung.

Durch die Weboberfläche kann das simulierte Fahrzeug von einem Desktop-PC oder Smartphone aus gesteuert werden. Gleichzeitig werden Kamerabild, Geschwindigkeit und Abstandsdaten dargestellt. Dadurch entsteht eine direkte Verbindung zwischen Simulation, Sensorik und externer Bedienung.

Die Dockerisierung verbessert zusätzlich die Reproduzierbarkeit des Projekts, da die für die Simulation benötigte Softwareumgebung gemeinsam mit dem Projekt bereitgestellt werden kann. Dadurch kann die Arbeit später leichter nachvollzogen, getestet und erweitert werden.
