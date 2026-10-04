RESTAURANT LOCATION GAME (Game Theory Elective Project)
Extended Hotelling model with 4 real-world modifications.
All customer data is SIMULATED (random seed 42).

REQUIREMENTS
- Python 3.10 or newer

HOW TO RUN
1. Open a terminal in the project folder.
2. Install libraries:
       pip install -r requirements.txt
3. Run the interactive app:
       python -m streamlit run src/app.py
   A browser tab opens (usually http://localhost:8501).
4. Use the sidebar sliders to set each restaurant's location, price,
   quality and delivery radius. The map and results update at once.
5. Click "Is this a Nash equilibrium?" to test the current setting.
6. Click "Find equilibrium" to run best-response search.

OTHER SCRIPTS
- python src/game.py      Prints the equilibrium of the modified game.
- python src/baseline.py  Prints the classical Hotelling equilibrium.
- python src/main.py      Shows a static plot of one scenario.

FILES
- src/game.py      Game engine (customers, roads, profit, best response, Nash)
- src/app.py       Streamlit interface
- src/baseline.py  Classical baseline for comparison
- src/main.py      Static demo plot

MODEL
- 10x10 town, 100 customers, 2 restaurants (A and B).
- Strategy = (x, y, price, quality, delivery radius).
  x,y in 0..10; price in {100,150,200,250}; quality 1..5; radius in {2,4,6,8}.
  9,680 strategies per restaurant.
- Modifications:
  1. Price and quality: cost = price + 10*travel - 5*quality
  2. Delivery: fee = 10 + 2*distance, available within the radius
  3. 2D clustering: town centre, shopping mall, business district
  4. Asymmetric roads: highway (0.7), normal (1.0), slow (1.5),
     bottleneck bridge (2.0); shortest-path travel cost
- Payoff: profit = (price - 50) * customers - 1000
- Customers choose the lowest-cost option; ties are split 50/50.
- Equilibrium: best-response iteration, then check that neither
  restaurant has a profitable unilateral deviation.

RESULT
- Classical game: both at (5,5), 50 customers each, profit 4000 each.
- Modified game: both at (5,5), price 100, quality 5, radius 8,
  50 customers each, profit 1500 each. Verified Nash equilibrium.

LIMITATION
- Quality has no cost in this model, so the equilibrium always
  picks the highest quality (5).

REPOSITORY
https://github.com/Nandhesh1309/GAME-THEORY-RESTAURANT-LOCATION-GAME-