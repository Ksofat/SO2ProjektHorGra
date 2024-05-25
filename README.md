# Gra Platformowa 2D - później utytułowana "Mortadella Hop"

"Mortadella Hop" to gra platformowa stworzona w języku 'Python' przy użyciu biblioteki 'Pygame', obsługująca wielowątkowość za pomocą modułu 'threading'. Oferuje dynamiczną rozgrywkę, w której gracz wciela się w postać skaczącą po ruchomych platformach i zbierającą mortadellę. Mapa gry nieustannie się przesuwa, a najmniejszy błąd może spowodować upadek i śmierć postaci.


![contept art](https://github.com/Ksofat/SO2ProjektHorGra/assets/163342588/a052ed83-30ba-49d2-a821-997d5db6542d)
Concept Art
![image](https://github.com/Ksofat/SO2ProjektHorGra/assets/163342588/39e4a5cb-fa22-4001-abe3-8f7604f570d0)
Grafika przedstawiająca co znajduje się na ekranie

### Wątki w projekcie:

**move_moving_platforms:** Zarządza poziomym ruchem platform, usuwa te, które zniknęły poza ekranem, i dodaje nowe w ich miejsce.

**generate_coins:** Generuje monety w miejscach dostępnych dla gracza, dbając o ich odpowiednią ilość na ekranie.

**play_background_music:** Odtwarza muzykę w pętli.

**player_physics:** Zarządza fizyką postaci (grawitacja, skoki) oraz kolizjami z platformami i monetami, aktualizując pozycję gracza i wynik.

**scroll_screen:** Zarządza płynnym przewijaniem ekranu w górę.


### Sekcje krytyczne:

**move_moving_platforms:** ***[MUTEKS]*** - Synchronizacja dostępu do listy moving_platforms, zapewniająca bezpieczne przesuwanie platform oraz zarządzanie ich tworzeniem i usuwaniem.

**player_physics:** ***[MUTEKS]*** - Synchronizacja dostępu do zmiennych player_pos, coins, score i moving_platforms, umożliwiająca bezpieczne aktualizowanie pozycji gracza, kolizji oraz wyniku.

**scroll_screen:** ***[MUTEKS]*** - Synchronizacja dostępu do zmiennych player_pos, terrain, moving_platforms i coins, zapewniająca bezpieczne przesuwanie ich pozycji podczas przewijania ekranu.
