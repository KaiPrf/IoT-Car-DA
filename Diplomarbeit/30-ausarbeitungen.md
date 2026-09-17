# Aufgabenstellung

## Auftraggeber

Der Auftraggeber dieser Diplomarbeit ist die HTL Leoben. Die Arbeit wird unter der Betreuung von Christoph Leitner, BEd., als Hauptbetreuer und DI (FH) Markus Zacharias als Nebenbetreuer durchgeführt.

## Ausgangssituation

Die allgemeine Aufgabenstellung entstand aus dem Interesse an vernetzten Systemen und insbesondere an der Kommunikation und Steuerung über ein externes Endgerät. Die Vernetzung verschiedener Komponenten stellt einen zentralen Bestandteil von IoT-Systemen dar und wurde im Unterricht nur teilweise praktisch behandelt.

Als Ausgangspunkt dient ein bereits vorhandenes physisches IoT-Car. Ursprünglich war vorgesehen, dieses Fahrzeug direkt weiterzuentwickeln und dessen Sensorik, Steuerung und Kommunikation in die Diplomarbeit einzubeziehen. Für die praktische Umsetzung war jedoch ein regelmäßiger Zugriff auf das Fahrzeug notwendig.

Da das IoT-Car über den Sommer nicht zur Verfügung gestellt werden konnte, war eine kontinuierliche Entwicklung und Erprobung am realen Fahrzeug nicht möglich. Um die Arbeit dennoch unabhängig von der Verfügbarkeit der Hardware durchführen und die geplanten Funktionen umsetzen zu können, wurde der Schwerpunkt auf eine digitale Simulation verlagert.

Das IoT-Car wird dafür in einer virtuellen Umgebung nachgebildet. Neben dem Fahrzeug selbst werden auch die Steuerung, die benötigte Sensorik sowie die Kommunikation mit einer externen Benutzeroberfläche simuliert. Dadurch können die grundlegenden Funktionen des ursprünglich geplanten Systems weiterhin entwickelt und getestet werden.

Die Simulation bildet dabei die wesentlichen Komponenten eines vernetzten Systems ab:

- ein Fahrzeugmodell als zu steuerndes System
- Sensoren zur Erfassung von Umgebungs- und Fahrzeugdaten
- eine Kommunikationsschicht zur Übertragung von Daten und Steuerbefehlen
- eine Steuerungslogik zur Verarbeitung der Eingaben
- eine externe Bedienoberfläche für Desktop und Smartphone

Für die Umsetzung wird ROS 2 als zentrale Kommunikations- und Steuerungsplattform eingesetzt. Die Fahrzeug- und Umgebungssimulation erfolgt mit Gazebo Sim. Die einzelnen Bestandteile werden modular aufgebaut, sodass Fahrzeugmodell, Sensorik, Steuerung und Benutzeroberfläche unabhängig voneinander entwickelt und getestet werden können.

Die Simulation stellt damit nicht nur eine Ersatzlösung für den fehlenden Zugriff auf das physische Fahrzeug dar, sondern schafft gleichzeitig eine reproduzierbare Entwicklungsumgebung. Die dabei entwickelte Steuerungs- und Kommunikationsstruktur kann später als Grundlage dafür dienen, die Funktionen auf das reale IoT-Car zu übertragen.
## Aufgabenstellung

Im Rahmen der Diplomarbeit soll eine funktionsfähige Simulation eines ursprünglich physisch geplanten IoT-Cars entwickelt werden. Da das reale Fahrzeug während des für die Umsetzung vorgesehenen Zeitraums nicht durchgehend zur Verfügung stand, werden die geplanten Funktionen in einer virtuellen Entwicklungsumgebung umgesetzt.

Ziel ist es, das Fahrzeugverhalten, die Sensorik, die Steuerungslogik sowie die Kommunikation mit einer externen Benutzeroberfläche möglichst modular nachzubilden. Das simulierte Fahrzeug soll innerhalb einer virtuellen Testumgebung steuerbar sein und relevante Fahrzeug- und Umgebungsdaten bereitstellen.

Die Aufgabe umfasst dabei insbesondere:

- Erstellung eines digitalen Fahrzeugmodells
- Umsetzung von Antrieb und Ackermann-Lenkung
- Integration einer Frontkamera
- Integration eines frontseitigen Abstandssensors
- Erfassung der Fahrzeuggeschwindigkeit
- Kommunikation der einzelnen Komponenten über ROS 2
- Entwicklung einer zentralen Steuerungslogik
- Entwicklung einer webbasierten Benutzeroberfläche
- Steuerung über Desktop-PC und Smartphone
- Übertragung von Kamerabild und Telemetriedaten an die Benutzeroberfläche
- Erstellung einer virtuellen Testumgebung in Gazebo Sim
- Bereitstellung der Simulation in einer Docker-Umgebung
- Dokumentation des technischen Aufbaus, der eingesetzten Komponenten und der praktischen Umsetzung

Das Ergebnis soll eine nachvollziehbare und reproduzierbare Simulationsplattform sein, mit der die grundlegenden Funktionen des ursprünglich vorgesehenen physischen IoT-Cars unabhängig von der vorhandenen Hardware entwickelt, getestet und demonstriert werden können.
