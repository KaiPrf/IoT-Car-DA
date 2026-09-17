# Projekthandbuch
\textauthor{Chloe Pripfl}

## Entwicklungsplan

### Projektauftrag

Im Rahmen der Diplomarbeit wird eine funktionsfähige Simulation eines IoT-Cars entwickelt. Ursprünglich war vorgesehen, das bereits vorhandene physische IoT-Car direkt weiterzuentwickeln. Da das Fahrzeug während des für die Umsetzung vorgesehenen Zeitraums nicht durchgehend zur Verfügung stand, wurde die praktische Umsetzung auf eine digitale Simulation verlagert.

Die Simulation soll die wesentlichen Funktionen des ursprünglich geplanten Systems nachbilden. Dazu gehören ein steuerbares Fahrzeugmodell, Sensorik, eine zentrale Kommunikations- und Steuerungsstruktur sowie eine externe Benutzeroberfläche für Desktop-PC und Smartphone.

Als technische Basis werden ROS 2 und Gazebo Sim eingesetzt. Die einzelnen Komponenten werden modular aufgebaut und über definierte Schnittstellen miteinander verbunden. Zusätzlich wird das Gesamtsystem in einer Docker-Umgebung bereitgestellt, um eine möglichst einfache und reproduzierbare Ausführung zu ermöglichen.

### Projektziele

Ziel des Projekts ist die Erstellung einer funktionsfähigen und nachvollziehbaren Simulationsplattform für ein IoT-Car.

Die wichtigsten Projektziele sind:

- Erstellung eines digitalen Fahrzeugmodells
- Umsetzung von Antrieb und Ackermann-Lenkung
- Integration einer Frontkamera
- Integration eines frontseitigen Abstandssensors
- Erfassung der Fahrzeuggeschwindigkeit
- Kommunikation zwischen den Komponenten über ROS 2
- Entwicklung einer zentralen Steuerungslogik
- Erstellung einer webbasierten Benutzeroberfläche
- Steuerung über Desktop-PC und Smartphone
- Übertragung von Kamerabild und Telemetriedaten
- Aufbau einer virtuellen Testumgebung in Gazebo Sim
- Bereitstellung der Anwendung in einer Docker-Umgebung
- nachvollziehbare Dokumentation der technischen Umsetzung

Das Gesamtsystem soll so aufgebaut sein, dass die einzelnen Bestandteile unabhängig voneinander erweitert oder ausgetauscht werden können.

### Nicht-Ziele bzw. nicht Inhalte

Nicht Bestandteil des Projekts sind:

- Entwicklung oder Fertigung eigener Fahrzeughardware
- vollständiger Umbau des vorhandenen physischen IoT-Cars
- Entwicklung eigener Kommunikationsprotokolle
- sicherheitszertifizierte Fahrzeugsteuerung
- vollständige autonome Navigation
- komplexe Bildverarbeitung oder Objekterkennung
- Optimierung für einen industriellen Produktiveinsatz
- vollständige Abbildung aller möglichen IoT-Anwendungsfälle
- industrielle Skalierung oder Hochverfügbarkeit

Der Schwerpunkt liegt auf einer technisch nachvollziehbaren Simulation und nicht auf der Entwicklung eines marktreifen Produkts.

### Projektnutzen

Durch die Simulation kann die geplante IoT-Car-Architektur unabhängig von der Verfügbarkeit des physischen Fahrzeugs entwickelt und getestet werden. Dadurch ist es möglich, Steuerung, Sensorik, Kommunikation und Benutzeroberfläche in einer kontrollierten Umgebung gemeinsam zu untersuchen.

Ein weiterer Vorteil besteht in der Reproduzierbarkeit. Das Fahrzeugmodell und die Testumgebung können jederzeit neu gestartet werden, ohne dass dafür ein reales Fahrzeug aufgebaut oder verfügbar sein muss. Änderungen an Software, Sensorik oder Steuerungsverhalten können dadurch schnell getestet werden.

Die modulare Struktur erleichtert außerdem spätere Erweiterungen. Einzelne Komponenten können angepasst werden, ohne das gesamte System neu entwickeln zu müssen. Durch die Dockerisierung wird zusätzlich eine standardisierte Laufzeitumgebung geschaffen, wodurch die Simulation auf anderen geeigneten Systemen einfacher bereitgestellt werden kann.


### Projektauftraggeber

Auftraggeber dieser Diplomarbeit ist die HTL Leoben.

## Projektorganisation

### Projektbeteiligte

| Vorname | Nachname | Organisation | Kontaktinfos |
|:--|:--|:--|:--|
| Chloe | Pripfl | HTL Leoben | Telefonnummer: +43 660 5460451 |

## Projektrisiken

| Risiko | Auswirkung | Maßnahme |
|:--|:--|:--|
| Physisches IoT-Car steht nicht zur Verfügung | Ursprünglich geplante Entwicklung am realen Fahrzeug kann nicht durchgeführt werden | Verlagerung der Umsetzung auf eine digitale Simulation |
| Unzureichende Simulationsperformance | Instabiles Fahrverhalten, verzögerte Sensorwerte oder niedrige Bildrate | Optimierung der Simulationsparameter und Nutzung von GPU-Unterstützung |
| Fehlerhafte Fahrzeugphysik | Unnatürliches Fahr- oder Lenkverhalten | Schrittweise Anpassung von Fahrzeuggeometrie, Gelenken, Dämpfung und Controllerparametern |
| Probleme bei der Sensorintegration | Kamera- oder Distanzdaten werden fehlerhaft oder nicht bereitgestellt | Sensoren getrennt testen und Daten über ROS-2-Topics kontrollieren |
| Netzwerkprobleme zwischen WSL, Docker und Endgeräten | Weboberfläche ist von Smartphone oder PC nicht erreichbar | Netzwerkpfade getrennt testen und Portfreigaben kontrollieren |
| Abhängigkeiten zwischen ROS 2, Gazebo und ros2_control | Komponenten starten nicht oder sind untereinander inkompatibel | Verwendung einer fest definierten Softwareumgebung und anschließende Dockerisierung |
| Fehler in der webbasierten Steuerung | Steuerbefehle oder Telemetriedaten werden nicht korrekt übertragen | WebSocket-Verbindungen und Eingabeverarbeitung getrennt testen |

## Anwendungsfälle

### Fahrzeug steuern

#### Kurzbeschreibung

Der Benutzer steuert das simulierte IoT-Car über die Weboberfläche. Dabei können Beschleunigung, Bremsen und Lenkung beeinflusst werden.

#### Trigger

Der Benutzer öffnet die Steuerungsoberfläche und gibt einen Fahrbefehl ein.

#### Vorbedingung

Die Simulation, die ROS-2-Komponenten und der Webserver sind gestartet.

#### Nachbedingung

Das Fahrzeug reagiert auf die Eingabe und bewegt beziehungsweise lenkt entsprechend des Steuerbefehls.

#### Akteure

- Benutzer
- Weboberfläche
- Steuerungslogik
- Fahrzeugsimulation

#### Standardablauf

1. Der Benutzer öffnet die Steuerungsoberfläche.
2. Der Benutzer gibt einen Lenk-, Gas- oder Bremsbefehl ein.
3. Die Weboberfläche überträgt die Eingabe an das System.
4. Die Steuerungslogik verarbeitet den Befehl.
5. Der Fahrzeugcontroller setzt den Befehl in der Simulation um.
6. Das Fahrzeug verändert Geschwindigkeit oder Fahrtrichtung.

#### Fehlersituationen

- Verbindung zur Simulation ist unterbrochen.
- Steuerbefehle werden nicht innerhalb der vorgesehenen Zeit empfangen.
- Der Fahrzeugcontroller ist nicht aktiv.

#### Systemzustand im Fehlerfall

Das Fahrzeug erhält keine neuen Fahrbefehle und wird nicht weiter aktiv beschleunigt.

### Kamerabild anzeigen

#### Kurzbeschreibung

Der Benutzer kann das von der simulierten Frontkamera erzeugte Bild direkt in der Weboberfläche betrachten.

#### Trigger

Der Benutzer öffnet die Steuerungsoberfläche.

#### Vorbedingung

Die Simulation und der Kamerasensor sind aktiv.

#### Nachbedingung

Das aktuelle Kamerabild wird in der Weboberfläche dargestellt.

#### Akteure

- Benutzer
- Gazebo-Kamera
- ROS 2
- Webserver
- Weboberfläche

#### Standardablauf

1. Die simulierte Kamera erzeugt Bilddaten.
2. Die Bilddaten werden über ROS 2 bereitgestellt.
3. Der Webserver verarbeitet die aktuellen Kamerabilder.
4. Die Daten werden über eine WebSocket-Verbindung an den Browser übertragen.
5. Das Bild wird in der Benutzeroberfläche dargestellt.

#### Fehlersituationen

- Kamerasensor liefert keine Bilddaten.
- WebSocket-Verbindung wird unterbrochen.
- Webserver ist nicht erreichbar.

#### Systemzustand im Fehlerfall

Die Fahrzeugsteuerung kann weiterhin verfügbar sein, das Kamerabild wird jedoch nicht oder nicht aktuell dargestellt.

### Telemetriedaten anzeigen

#### Kurzbeschreibung

Geschwindigkeit und Abstand zum nächsten Hindernis werden während der Fahrt in der Weboberfläche dargestellt.

#### Trigger

Die Simulation ist aktiv und erzeugt Sensor- beziehungsweise Fahrzeugdaten.

#### Vorbedingung

Geschwindigkeits- und Abstandsauswertung sind gestartet.

#### Nachbedingung

Die aktuellen Messwerte werden in der Weboberfläche angezeigt.

#### Akteure

- Geschwindigkeitssensor
- Abstandssensor
- ROS 2
- Webserver
- Weboberfläche
- Benutzer

#### Standardablauf

1. Die Simulation stellt die benötigten Rohdaten bereit.
2. Die ROS-2-Nodes verarbeiten die Daten.
3. Geschwindigkeit und Abstand werden auf eigenen Topics veröffentlicht.
4. Der Webserver empfängt die aktuellen Werte.
5. Die Werte werden an die Weboberfläche übertragen.
6. Der Benutzer sieht die aktuellen Telemetriedaten.

#### Fehlersituationen

- Sensordaten fehlen oder sind ungültig.
- Verbindung zwischen ROS 2 und Webserver ist unterbrochen.
- WebSocket-Verbindung zum Browser ist nicht aktiv.

#### Systemzustand im Fehlerfall

Die betroffenen Messwerte werden nicht aktualisiert beziehungsweise als ungültig behandelt.
