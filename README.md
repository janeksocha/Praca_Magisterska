# Analiza sygnału EKG oraz parametrów HRV u zawodników szermierki

## Opis projektu

Projekt został zrealizowany w ramach pracy magisterskiej na Wydziale Mechatroniki Politechniki Warszawskiej.

Celem pracy była analiza sygnału elektrokardiograficznego (EKG) oraz parametrów zmienności rytmu serca (HRV) w kontekście oceny reakcji organizmu na wysiłek fizyczny oraz procesów regeneracyjnych u zawodników szermierki.

Do rejestracji sygnału EKG wykorzystano przenośny sensor **Movesense ECG Heart Rate Monitor**, umożliwiający wykonywanie pomiarów podczas aktywności sportowej. Badanie obejmowało zawodników wyczynowo trenujących szermierkę, w tym zawodników Kadry Narodowej seniorów w szpadzie, oraz grupę kontrolną. Oprócz danych fizjologicznych zebrano również informacje ankietowe dotyczące samopoczucia, zmęczenia, poziomu energii i regeneracji.

Surowe dane EKG, ankiety oraz wygenerowane wyniki nie są przechowywane w repozytorium. Zostały wykluczone z kontroli wersji ze względu na charakter danych badawczych.

## Cele pracy

W ramach projektu zrealizowano następujące zadania:

- rejestrację sygnałów EKG podczas aktywności sportowej,
- ocenę jakości zarejestrowanych sygnałów,
- wstępne przetwarzanie i oczyszczanie sygnału EKG,
- detekcję załamków R,
- wyznaczenie odstępów RR,
- obliczenie wybranych parametrów HRV w dziedzinie czasu i częstotliwości,
- porównanie parametrów HRV podczas walki i regeneracji,
- porównanie grupy badawczej i kontrolnej,
- analizę zależności pomiędzy parametrami HRV a wynikami ankiet,
- zastosowanie metod uczenia maszynowego do predykcji wybranych wskaźników ankietowych.

## Dane pomiarowe

Sygnały EKG rejestrowano za pomocą urządzenia Movesense ECG Heart Rate Monitor. Dane eksportowano do plików zawierających czas pomiaru oraz wartości sygnału EKG.

W analizie przyjęto częstotliwość próbkowania **200 Hz**, odpowiadającą odstępowi 0,005 s pomiędzy kolejnymi próbkami.

Dane analizowano w dwóch okresach:

- podczas walki szermierczej,
- podczas regeneracji, określonej jako ostatnie trzy minuty rejestracji.

W badaniu zgromadzono **35 zapisów EKG**, które po przeprowadzeniu kontroli jakości zostały zakwalifikowane do dalszej analizy. Żaden z pomiarów nie został odrzucony.

## Przetwarzanie sygnału EKG

Proces analizy obejmował wczytanie danych, przygotowanie sygnału do analizy, jego oczyszczenie, detekcję załamków R oraz wyznaczenie odstępów RR.

Do przetwarzania sygnału i detekcji załamków R wykorzystano bibliotekę **NeuroKit2**. Na podstawie wykrytych załamków R obliczano parametry HRV.

Ocena jakości sygnałów obejmowała analizę podstawowych parametrów sygnału, kontrolę potencjalnych artefaktów oraz wizualną inspekcję zapisów. Dla wszystkich 35 rejestracji uzyskano status umożliwiający dalsze przetwarzanie, a algorytm NeuroKit2 poprawnie wykrywał załamki R w analizowanych zapisach.

## Parametry HRV

W pracy analizowano następujące parametry:

### Parametry w dziedzinie czasu

- **RMSSD** – pierwiastek ze średniej kwadratów różnic pomiędzy kolejnymi odstępami RR,
- **SDNN** – odchylenie standardowe odstępów NN/RR,
- **MeanNN** – średnia wartość odstępów NN/RR.

### Parametry w dziedzinie częstotliwości

- **HF** – składowa wysokoczęstotliwościowa,
- **LF** – składowa niskoczęstotliwościowa,
- **LF/HF** – stosunek mocy składowej LF do HF.

Parametry były obliczane oddzielnie dla okresu walki oraz okresu regeneracji.

## Analiza statystyczna

Analizę statystyczną przeprowadzono w języku Python z wykorzystaniem bibliotek `pandas`, `numpy`, `scipy`, `matplotlib` oraz `seaborn`.

Wykonano:

- statystyki opisowe,
- ocenę normalności rozkładów za pomocą testu Shapiro–Wilka,
- porównanie parametrów HRV pomiędzy walką i regeneracją,
- porównanie grupy badawczej i kontrolnej,
- analizę zależności pomiędzy parametrami HRV i wynikami ankiet,
- wizualizację rozkładów danych oraz zależności pomiędzy zmiennymi.

Dobór testów statystycznych zależał od charakteru danych i wyniku oceny normalności rozkładu.

## Uczenie maszynowe

W pracy zastosowano metody uczenia maszynowego w celu sprawdzenia, czy parametry HRV mogą być wykorzystane do predykcji wybranych wskaźników uzyskanych z ankiet.

Wykorzystano modele:

- regresję liniową,
- drzewo decyzyjne,
- Random Forest,
- Support Vector Regression (SVM/SVR).

Do oceny modeli wykorzystano:

- **MAE** – średni błąd bezwzględny,
- **RMSE** – pierwiastek z błędu średniokwadratowego,
- **R²** – współczynnik determinacji.

Zastosowano również walidację **Leave-One-Out Cross-Validation (LOOCV)** oraz analizę ważności cech dla modelu Random Forest.

Wyniki wskazały na ograniczoną zdolność predykcyjną modeli wykorzystujących wyłącznie parametry HRV. Oznacza to, że HRV może stanowić wartościowe źródło informacji, ale samo w sobie nie jest wystarczające do pełnej predykcji subiektywnie ocenianego poziomu zmęczenia czy energii.

## Najważniejsze wyniki

Analiza danych wykazała, że:

- wszystkie 35 zarejestrowanych sygnałów EKG spełniło przyjęte kryteria jakości i zostało wykorzystane w dalszej analizie,
- pomiędzy okresem walki i regeneracji występowały istotne statystycznie różnice dla wybranych parametrów HRV,
- największą różnicę zaobserwowano dla parametru **MeanNN**, którego średnia wartość wzrosła z 389,06 ms podczas walki do 491,66 ms w okresie regeneracji,
- istotne różnice stwierdzono również dla **RMSSD, LF oraz LF/HF**,
- dla **SDNN oraz HF** nie stwierdzono istotnych statystycznie różnic pomiędzy walką i regeneracją,
- w porównaniu grupy badawczej i kontrolnej istotną statystycznie różnicę stwierdzono dla **SDNN podczas aktywności sportowej**, natomiast dla pozostałych analizowanych parametrów nie wykazano istotnych różnic,
- zależności pomiędzy parametrami HRV a wynikami ankiet nie były na tyle silne, aby umożliwić pełną ocenę stanu zawodnika wyłącznie na podstawie HRV,
- modele uczenia maszynowego miały ograniczoną zdolność predykcyjną, co wskazuje na potrzebę zwiększenia liczby obserwacji i uwzględnienia dodatkowych zmiennych.

## Wnioski

Przeprowadzone badania wskazują, że analiza HRV może dostarczać użytecznych informacji dotyczących reakcji organizmu na wysiłek fizyczny oraz zmian zachodzących w okresie regeneracji.

Połączenie analizy sygnału EKG, metod statystycznych i uczenia maszynowego stanowi potencjalnie użyteczne podejście do monitorowania sportowców. Jednocześnie uzyskane wyniki pokazują, że parametry HRV powinny być traktowane jako **uzupełniające źródło informacji**, a nie jako samodzielne narzędzie do kompleksowej oceny zmęczenia i regeneracji.

## Ograniczenia

Do najważniejszych ograniczeń pracy należały:

- ograniczona liczba obserwacji,
- duża zmienność indywidualna pomiędzy zawodnikami,
- wykorzystanie subiektywnych ocen ankietowych,
- ograniczenie analizy regeneracji do ostatnich trzech minut rejestracji,
- wykorzystanie przede wszystkim parametrów HRV wyznaczonych z sygnału EKG,
- brak dodatkowych zmiennych fizjologicznych i treningowych,
- ograniczona liczba obserwacji dostępnych do budowy modeli uczenia maszynowego.

Większy zbiór danych oraz uwzględnienie dodatkowych informacji, takich jak obciążenie treningowe, jakość snu, parametry wydolnościowe czy inne dane fizjologiczne, mogłyby zwiększyć wartość przyszłych analiz i skuteczność modeli predykcyjnych.

## Struktura repozytorium

```text
Movesense/
├── src/
│   ├── __init__.py
│   ├── data_preprocess.py
│   ├── hrv_analysis.py
│   ├── hrv_metrics.py
│   ├── load_data.py
│   ├── machine_learning_analysis.py
│   ├── statistics_analysis.py
│   └── visualize.py
├── .gitignore
├── requirements.txt
└── README.md
```

Foldery zawierające dane pomiarowe i wyniki analizy są wyłączone z repozytorium.

## Wykorzystane technologie

- **Python**
- **pandas** – przetwarzanie danych,
- **NumPy** – obliczenia numeryczne,
- **SciPy** – analiza statystyczna,
- **NeuroKit2** – przetwarzanie sygnału EKG, detekcja załamków R i analiza HRV,
- **scikit-learn** – modele uczenia maszynowego i walidacja,
- **Matplotlib** – wizualizacja danych,
- **Seaborn** – wizualizacja statystyczna,
- **openpyxl** – obsługa plików Excel.

## Uruchomienie projektu

Kod został przygotowany w języku Python. Lista wymaganych bibliotek znajduje się w pliku `requirements.txt`.

Odtworzenie pełnej analizy wymaga dostępu do odpowiednich danych wejściowych. Ze względu na charakter danych badawczych surowe zapisy EKG, ankiety oraz wygenerowane wyniki nie zostały umieszczone w publicznej części repozytorium.

## Autor

**Jan Socha**

Wydział Mechatroniki  
Politechnika Warszawska

Praca magisterska:

**„Analiza sygnału EKG oraz parametrów HRV u zawodników szermierki z wykorzystaniem metod statystycznych i uczenia maszynowego”**

Promotor: **dr hab. inż. Marcel Młyńczak**
