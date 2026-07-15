# Teilaufgabe Schüler Pripfl

\textauthor{Chloe Pripfl}



## Einleitung

Das IoT-Car hat bislang noch keine produktive Verwendung gefunden. Zu Beginn der Diplomarbeit kann das Fahrzeug ausschließlich mithilfe einer Carson ModelSport Fernbedienung gesteuert werden. Zudem sind die Jumperkabel, welche die Sensoren mit dem verbauten Raspberry Pi verbinden, aktuell nicht angeschlossen.

Ziel dieser Teilaufgabe ist es, eine technische Basis für die weitere Arbeit zu schaffen. Dazu werden folgende Schritte umgesetzt:

* Wiederverbinden der Jumperkabel zu den Sensoren
* Aufsetzen von ROS 2 auf dem Raspberry Pi
* Einbindung und Bereitstellung der Kamerasicht des Fahrzeugs
* Implementierung einer Smartphone‑basierten Steuerung



## Theorieteil

### ROS 2

#### Was ist ROS?

ROS (Robot Operating System) ist ein Open‑Source‑Framework, das Bibliotheken, Werkzeuge und Kommunikationsmechanismen zur Entwicklung von Roboteranwendungen bereitstellt. Es vereinfacht die Programmierung komplexer Systeme und ermöglicht eine modulare, wiederverwendbare und skalierbare Softwarearchitektur.

[@ROS2]

#### Grundidee und Architektur (ROS vs. ROS 2)

ROS basiert auf einem verteilten System aus sogenannten **Nodes**. Ein Node ist ein einzelnes Programm, das eine klar definierte Teilaufgabe übernimmt, beispielsweise Sensorauswertung oder Motorsteuerung. In ROS 2 wurde dieses Konzept erweitert: Innerhalb eines Prozesses können mehrere Nodes betrieben werden. Zusätzlich wurden **Lifecycle‑Nodes** eingeführt, die definierte Zustände wie *unconfigured*, *inactive* und *active* besitzen.

In ROS 1 existiert ein zentraler **Master**, der für die Namensregistrierung und ‑auflösung im sogenannten Computation Graph zuständig ist. Ohne diesen Master können Nodes einander nicht finden und nicht miteinander kommunizieren. ROS 2 verzichtet auf einen zentralen Master; Discovery und Kommunikation erfolgen vollständig dezentral, was die Ausfallsicherheit erhöht.

Der **Parameter Server** dient zur Speicherung von Konfigurationswerten in Form von Schlüssel‑Wert‑Paaren. Während dieser in ROS 1 Teil des Masters ist, sind Parameter in ROS 2 node‑lokal organisiert.

Die Kommunikation zwischen Nodes erfolgt über **Messages**, welche strukturierte und typisierte Daten enthalten. Unterstützt werden primitive Datentypen, Arrays sowie verschachtelte Strukturen.

Messages werden über ein Transportsystem mit Publish‑/Subscribe‑Semantik übertragen:

* Ein Node veröffentlicht Daten auf einem **Topic** (*publish*).
* Andere Nodes können dieses Topic abonnieren (*subscribe*).

ROS 2 erweitert dieses Modell um **Quality‑of‑Service‑Mechanismen (QoS)**, mit denen Zuverlässigkeit, Latenz und Echtzeitverhalten gezielt gesteuert werden können.

Für klassische Anfrage‑/Antwort‑Kommunikation stehen **Services** zur Verfügung. Ein Service besteht aus einer Request‑ und einer Reply‑Message. Für langlaufende Aufgaben mit Statusrückmeldungen werden in ROS 2 zusätzlich **Actions** verwendet.

**ROS Bags** sind Dateiformate zum Aufzeichnen und Wiedergeben von ROS‑Nachrichten. Sie werden insbesondere zur Analyse, Fehlersuche und Entwicklung genutzt. ROS 2 verwendet hierfür ein neues Backend mit Unterstützung mehrerer Speicherformate, wie z. B. SQLite.

[@ROS-Architektur] & [@ROSvsROS2-Architektur]



#### Warum ROS 2?

ROS 2 wurde entwickelt, um den Anforderungen moderner Robotik‑ und IoT‑Systeme gerecht zu werden. Ein wesentlicher Vorteil ist die dezentrale Architektur ohne zentralen Master, wodurch das System robuster gegenüber Ausfällen wird.

Ein weiterer wichtiger Aspekt ist die verbesserte Echtzeitfähigkeit. Durch QoS‑Einstellungen und die Unterstützung von Echtzeit‑Betriebssystemen kann ROS 2 auch in zeitkritischen Anwendungen eingesetzt werden. Für das IoT‑Car bedeutet dies eine zuverlässigere Steuerung und stabilere Verarbeitung von Sensor‑ und Kameradaten.

Zusätzlich ist ROS 2 besser für Embedded‑Plattformen wie den Raspberry Pi geeignet. Der geringere Ressourcenverbrauch, moderne Sicherheitsmechanismen und flexible Kommunikationsparameter machen ROS 2 zur idealen Wahl für dieses Projekt.



#### ROS 2 Jazzy Jalisco

In dieser Diplomarbeit wird **ROS 2 Jazzy Jalisco** verwendet. Dabei handelt es sich um eine Long‑Term‑Support‑(LTS)‑Version, die über einen längeren Zeitraum mit Sicherheits‑ und Fehlerupdates versorgt wird.

ROS 2 Jazzy basiert auf **Ubuntu 24.04 LTS** und nutzt aktuelle Systembibliotheken sowie moderne Compiler. Dadurch werden eine höhere Performance, bessere Sicherheit und eine gute Kompatibilität mit aktueller Hardware gewährleistet.

In Kombination mit einem Echtzeit‑Kernel (PREEMPT‑RT) eignet sich ROS 2 Jazzy besonders für zeitkritische Anwendungen wie die Steuerung eines IoT‑Cars. Steuerbefehle, Sensordaten und Kamerastreams können mit geringerer Latenz und höherer Zuverlässigkeit verarbeitet werden.

Darüber hinaus bietet Jazzy eine ausgereifte Integration der DDS‑Middleware (Data Distribution Service), welche eine skalierbare und flexible Kommunikation zwischen verteilten Komponenten ermöglicht.



### Raspberry‑Pi‑Image

Das **ros‑realtime‑rpi4‑image** ist ein vorkonfiguriertes Betriebssystem‑Image für Raspberry‑Pi‑Geräte, das speziell für Robotik‑ und Echtzeit‑Anwendungen mit ROS 2 entwickelt wurde.

#### Enthaltene Software und Eigenschaften

Das Image basiert auf **Ubuntu Server 24.04 (64‑Bit)** und verzichtet bewusst auf eine grafische Benutzeroberfläche. Dadurch werden Systemressourcen geschont, was insbesondere auf leistungsschwächeren Plattformen wie dem Raspberry Pi 3 von Vorteil ist.

ROS 2 Jazzy ist vollständig vorinstalliert. Nach dem ersten Start steht die komplette ROS‑2‑Laufzeitumgebung sofort zur Verfügung, inklusive aller zentralen Werkzeuge zur Paketverwaltung und Kommunikation.

Ein wesentliches Merkmal ist der verwendete Linux‑Kernel mit **PREEMPT‑RT‑Patch**, der nicht‑deterministische Verzögerungen reduziert und zeitkritische Prozesse bevorzugt behandelt. Dies verbessert die Stabilität von Steuerungs‑ und Kommunikationsabläufen erheblich.

Der SSH‑Zugriff ist standardmäßig aktiviert. Der voreingestellte Benutzername lautet *ubuntu*, ebenso das initiale Passwort, welches beim ersten Login geändert werden muss.



### Kameraanbindung in ROS 2

Die Kamera des IoT‑Cars wird in ROS 2 als eigener Node betrieben. Dieser erfasst kontinuierlich Bilddaten und veröffentlicht diese als Messages auf einem Topic, beispielsweise */camera/image_raw*.

Für die Bilddaten werden standardisierte Message‑Typen aus dem Paket **sensor_msgs** verwendet. Dadurch ist eine einfache Weiterverarbeitung der Kameradaten möglich, etwa für spätere Erweiterungen wie Hinderniserkennung oder Spurverfolgung.



### Smartphone‑Anbindung und IoT‑Konzepte

Die Steuerung des IoT‑Cars über ein Smartphone stellt eine typische IoT‑Anwendung dar. Das Smartphone fungiert als Benutzeroberfläche, während der Raspberry Pi die eigentliche Steuerungslogik übernimmt.

Die Kommunikation kann über das Protokoll **MQTT** erfolgen, welches speziell für ressourcenschonende und zuverlässige Nachrichtenübertragung entwickelt wurde. Steuerbefehle werden dabei als Nachrichten an definierte Topics gesendet und von einem ROS‑2‑Node auf dem Raspberry Pi empfangen und umgesetzt.

Durch die Kombination von ROS 2 und MQTT entsteht ein modulares und flexibel erweiterbares System, das sich für Fernsteuerung, Statusanzeigen und spätere autonome Funktionen eignet.



# Praxisteil




