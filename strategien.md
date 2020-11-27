# Strategien Battle Snake

### Pfadsuche
- möglichst wenig A* Star search verwenden da kostenintensiv
    - Pfad über die Runden solange verwenden bis es keinen Sinn mehr macht
    - Pfad anpassen an Position und Verhalten der anderen Snakes
### Moves    
- moves strategisch verwenden das die Kollisionen nicht zu unserem Nachteil passieren:
    - {self-collision, body-collision, head-to-head-collision}

- moves so wählen das Schlange nicht out of bounds geht
    - bei Royal verschiedene Wertigkeit der Felder durch Genom 

- Heuristiken für die Sicherheit von verschiedenen Moves
    - wo sind Köpfe der anderen Schlangen
    - Deadlocks vermeiden
    - nicht verhungern

- Bewertung des Feldes und der Moves:
    - Felder des Spiels mit Rewards versehen (per Genom anpassen?)
    - Seiten sind gefährlich da man gefangen wird
    - können aber auch hilfreich sein gegner einzuschließen

### Agents
- (Deep) Q-Learning Agent auf Basis von Rewards des Spielfeldes
- MCTS als Strategie-Helfer
- Gegnerische Agents am Anfang beobachten um dann Verhalten vorherzusagen

### Grundlegende Strategie:
- klein bleiben und provozieren das große Schlange sich selbst schlägt
    - chase-tale wenn nichts passiert
    - body-collision provozieren wenn gegner in der Nähe
    - Sicherheit von Essen einbeziehen und dann erst spät zuschlagen
        - Schätzer als NN , ...
        
- groß werden und kleine Schlange in die Enge drängen

- am Anfang hungry dann agressive, chase tail falls Zeit abgelaufen oder keine andere Idee
    - genom von Spielfaktoren (Spiellänge, Schlangenlänge, Health, Gegnerstats) und anhand dessen eine Algorithmus Auswahl?

### Technische Umsetzung
- anhand von time die Zeit stoppen und solange iterieren bis 400ms erreicht sind

- Parallelisierung der verschiedenen Algorithmen mit threading modul und multiprocessing
    - gleichzeitig losschicken und alle ergebnisse die zurückkommen nutzen