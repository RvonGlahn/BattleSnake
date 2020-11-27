# Strategien Battle Snake

### Pfadsuche
- möglichst wenig A* Star search verwenden da kostenintensiv
    - Pfad über die Runden solange verwenden bis es keinen Sinn mehr macht
    - Pfad anpassen an Position und Verhalten der anderen Snakes
    
- am Anfang hungry dann agressive, chase tail falls Zeit abgelaufen oder keine andere Idee
    - genom von Spielfaktoren (Spiellänge, Schlangenlänge, Gegnerstats) und anhand dessen eine Algorithmus Auswahl?
- moves strategisch verwenden das die Kollisionen nicht zu unserem Nachteil passieren:
    - {self-collision, body-collision, head-to-head-collision}
- moves so wählen das Schlange nicht out of bounds geht
    - bei Royal verschiedene Wertigkeit der Felder durch Genom 
- Parallelisierung der verschiedenen Algorithmen mit threading modul
- 