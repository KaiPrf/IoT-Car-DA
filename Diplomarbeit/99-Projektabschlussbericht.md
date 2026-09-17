\newpage

# Projektabschlussbericht
\textauthor{Chloe Pripfl}

## Erfolgsmessung

### Erreichung Leistungs-/Qualitätsziele

Das grundlegende Ziel dieser Diplomarbeit bestand darin, ein IoT-Car als funktionsfähige digitale Simulation umzusetzen und dabei zentrale Aspekte eines vernetzten Systems praktisch abzubilden. Dazu sollten Fahrzeugsteuerung, Sensorik, Kommunikation und eine externe Benutzeroberfläche miteinander verbunden werden.

Dieses Ziel konnte im Wesentlichen erreicht werden. Das Fahrzeug wurde in Gazebo Sim als digitales Modell umgesetzt und mit einer Ackermann-Lenkung sowie einem Hinterradantrieb ausgestattet. Zusätzlich wurden eine Frontkamera, ein frontseitiger Abstandssensor und eine Geschwindigkeitsauswertung integriert.

Die Kommunikation zwischen den einzelnen Komponenten erfolgt über ROS 2. Für die Steuerung wurde eine eigene Steuerungslogik entwickelt, welche Eingaben für Lenkung, Gas, Bremse und Not-Stopp verarbeitet.

Zusätzlich wurde eine webbasierte Benutzeroberfläche entwickelt. Über diese kann das Fahrzeug sowohl von einem Desktop-PC als auch von einem Smartphone gesteuert werden. Gleichzeitig werden Kamerabild, Geschwindigkeit und Abstand zum nächsten Hindernis angezeigt.

Im Verlauf der Entwicklung traten mehrere technische Herausforderungen auf. Dazu gehörten unter anderem die Simulationsperformance in einer virtuellen Maschine, das Fahrverhalten des Fahrzeugmodells, die Positionierung der Sensoren, die Übertragung des Kamerastreams sowie die Netzwerkkommunikation zwischen Windows, WSL2, Docker und mobilen Endgeräten.

Die ursprünglich geplante direkte Umsetzung am physischen IoT-Car konnte nicht durchgeführt werden, da während des notwendigen Entwicklungszeitraums kein durchgehender Zugriff auf das Fahrzeug möglich war. Durch die Verlagerung auf eine Simulation konnten die geplanten Funktionen dennoch umgesetzt und getestet werden.

Aus diesem Grund kann das ursprüngliche Projektziel – die Umsetzung und praktische Untersuchung eines vernetzten IoT-Car-Systems – insgesamt als erreicht betrachtet werden.

### Erreichung Terminziele

Da es sich bei dieser Arbeit um eine nachgebrachte Diplomarbeit handelt, wurde kein klassischer Projektablauf mit verbindlichen Meilensteinen und einem langfristig geplanten Terminplan geführt.

Die praktische Umsetzung wurde stattdessen schrittweise anhand der jeweils notwendigen technischen Aufgaben durchgeführt. Dabei kam es in mehreren Bereichen zu zusätzlichem Zeitaufwand, insbesondere bei der Einrichtung der Entwicklungsumgebung, der Optimierung des Fahrzeugverhaltens sowie bei der Netzwerk- und Docker-Konfiguration.

Trotz dieser zusätzlichen Aufwände konnten die für die Arbeit notwendigen technischen Funktionen umgesetzt und die Dokumentation fertiggestellt werden.

### Erreichung Kosten-/Aufwandsziele

Für die Durchführung dieses Projekts waren keine nennenswerten finanziellen Kosten erforderlich. Die gesamte Entwicklung erfolgte auf vorhandener Hardware sowie mit frei verfügbarer beziehungsweise Open-Source-Software.

Sowohl ROS 2 und Gazebo Sim als auch die benötigten Entwicklungswerkzeuge, WSL2 und Docker stehen kostenlos zur Verfügung. Daher entstanden für die technische Umsetzung keine wesentlichen zusätzlichen Kosten.

Der tatsächliche Aufwand des Projekts lag hauptsächlich im Zeitaufwand für Recherche, Entwicklung, Fehlersuche, Tests und Dokumentation.

## Reflexion / Lessons Learned

### Projektmanagement

Im Verlauf des Projekts zeigte sich, wie wichtig es ist, auf geänderte Rahmenbedingungen flexibel reagieren zu können. Ursprünglich war vorgesehen, direkt mit dem vorhandenen physischen IoT-Car zu arbeiten. Da das Fahrzeug jedoch nicht während des gesamten notwendigen Entwicklungszeitraums zur Verfügung stand, musste die praktische Umsetzung grundlegend angepasst werden.

Die Entscheidung, das IoT-Car stattdessen vollständig zu simulieren, ermöglichte es, die Arbeit unabhängig von der realen Hardware fortzusetzen und die geplanten Funktionen trotzdem umzusetzen.

Auch während der technischen Entwicklung mussten ursprüngliche Ansätze mehrfach angepasst werden. Beispiele dafür waren der Wechsel von einer klassischen virtuellen Maschine auf WSL2, Änderungen an der Fahrzeugphysik, Anpassungen an der Sensorik sowie die Umstellung des Kamerastreams.

Ein wichtiger Teil des Projektmanagements bestand daher darin, auftretende Probleme einzeln zu analysieren, Lösungsansätze zu testen und funktionierende Zwischenstände beizubehalten.

### Sonstige Lernerfahrungen

Während der Arbeit an diesem Projekt konnten umfangreiche praktische Kenntnisse in den Bereichen Robotik, Simulation, Netzwerkkommunikation und Softwareentwicklung gewonnen werden.

Dazu gehören unter anderem:

* Aufbau und Verwendung von ROS-2-Nodes und Topics
* Modellierung eines Fahrzeugs für Gazebo Sim
* praktische Umsetzung einer Ackermann-Lenkung
* Simulation und Verarbeitung von Sensorwerten
* Entwicklung einer zentralen Steuerungslogik
* Entwicklung einer webbasierten Benutzeroberfläche
* Übertragung von Steuer- und Telemetriedaten über WebSockets
* Netzwerkkommunikation zwischen Windows, WSL2, Docker und mobilen Endgeräten
* Containerisierung einer ROS-2- und Gazebo-Anwendung mit Docker
* systematische Fehlersuche in einem verteilten Softwaresystem

Besonders deutlich wurde, dass bei Simulationen auch kleine Parameteränderungen einen großen Einfluss auf das Verhalten des Systems haben können. Ein Beispiel dafür war die Dämpfung der Radgelenke, welche das Kurvenverhalten des Fahrzeugs stark beeinflusste.

Auch bei der Sensorik zeigte sich, dass neben der grundsätzlichen Integration auch Positionierung, Grenzfälle und die Verarbeitung der Rohdaten berücksichtigt werden müssen.

### Nachhaltigkeitsanalyse

Im Rahmen der Nachhaltigkeitsanalyse wird untersucht, inwiefern diese Diplomarbeit einen Bezug zu den Sustainable Development Goals (SDGs) der Vereinten Nationen aufweist.

Die Arbeit leistet insbesondere einen indirekten Beitrag zu folgenden Zielen:

**SDG 9 – Industrie, Innovation und Infrastruktur**

Die Arbeit beschäftigt sich mit modernen Technologien aus den Bereichen Robotik, IoT, Simulation und Containerisierung. Die Kombination dieser Technologien zeigt, wie vernetzte Systeme modular entwickelt, getestet und reproduzierbar bereitgestellt werden können.

**SDG 4 – Hochwertige Bildung**

Die Diplomarbeit dient als Lern- und Demonstrationsprojekt im Bereich IoT, Robotik und Softwareentwicklung. Die dokumentierten Ergebnisse können auch als Grundlage für zukünftige Schüler oder weitere Projekte verwendet werden.

Darüber hinaus basiert die gesamte Arbeit überwiegend auf frei verfügbaren beziehungsweise Open-Source-Technologien. ROS 2, Gazebo Sim und die verwendeten Entwicklungswerkzeuge können ohne zusätzliche Lizenzkosten eingesetzt werden.

Ein negativer Einfluss auf ökologische oder soziale Nachhaltigkeitsaspekte ist im Rahmen dieses Projekts nur in geringem Umfang zu erwarten. Für die Simulation wird zusätzliche Rechenleistung benötigt, insbesondere durch die 3D-Simulation und das Rendering. Gleichzeitig war keine zusätzliche Hardwareproduktion notwendig, da die Entwicklung vollständig auf bereits vorhandener Hardware durchgeführt wurde.
