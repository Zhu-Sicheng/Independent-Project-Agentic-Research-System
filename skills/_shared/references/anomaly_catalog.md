# Anomaly catalogue — mechanism seeds for factor hypotheses

Use this catalogue as a menu of **mechanisms**, not as a list of formulas. Each
row gives the economic story, the raw directional expectation, a sensible
horizon, the fields needed, and the conditions that break it. Adapt the story to
the universe and the fields actually available in the Agent-1 contract.

Direction column: `+` means the raw signal concept is expected to align with
higher forward returns, `-` means it aligns with lower forward returns.

## 1. Short-horizon reversal and pressure

| idea | mechanism | dir | horizon | fields | failure modes | origin |
|---|---|---|---|---|---|---|
| short-horizon reversal | short-term price pressure from uninformed demand mean-reverts as liquidity suppliers are compensated for absorbing inventory | - | 2-10d | close, returns | genuine information moves (earnings, guidance) | Lehmann 1990; Jegadeesh 1990 |
| overnight reversal | overnight moves are dominated by retail/attention flows and liquidity gaps, then partly reverse during the session | - | 1-5d | overnight_return, intraday_return, close | macro-regime shifts; persistent overnight news | Lou, Polk & Skouras 2019 |
| intraday momentum continuation | informed institutional execution within the day persists into the next session | + | 1-3d | intraday_return, close, volume | liquidity shocks; index rebalances | Heston, Korajczyk & Sadka 2010 |
| volume-shock reversal | abnormally high activity after a price move marks uninformed attention rather than information, so the move reverses | - | 3-10d | close, volume, amount | event-driven information spikes | Barber & Odean 2008; Gervais et al. 2001 |
| gap fade | opening gaps driven by overnight order imbalance fill once continuous trading provides liquidity | - | 1-3d | open, high, low, close | news gaps that carry information | Berkman et al. 2012 |
| illiquidity reversal | when liquidity is scarce, price concessions required to trade reverse once participation normalises | - | 5-20d | close, volume, amount, adv20 | persistent liquidity deterioration; delisting risk | Amihud 2002; Pastor & Stambaugh 2003 |

## 2. Momentum and anchoring

| idea | mechanism | dir | horizon | fields | failure modes | origin |
|---|---|---|---|---|---|---|
| cross-sectional momentum | gradual information diffusion and herding make recent winners outperform recent losers | + | 1-6m | close, returns | momentum crashes after regime breaks | Jegadeesh & Titman 1993 |
| 52-week-high anchoring | investors anchor on the 52-week high; proximity to it delays selling and sustains demand | + | 1-3m | close, high | strong bear regimes; small illiquid names | George & Hwang 2004 |
| time-series momentum | own past return predicts the instrument's future return in the same direction across asset classes | + | 1-12m | close, returns | choppy range regimes; volatility spikes | Moskowitz, Ooi & Pedersen 2012 |
| moving-average distance | price relative to a long moving average captures trend state; far-below prices attract mean-reverting demand, far-above prices signal crowding | +/- | 1-3m | close | violent reversals; structural breaks | Brock, Lakonishok & LeBaron 1992 |
| return consistency | a series of small same-sign moves reflects persistent accumulation rather than one-off jumps | + | 1-3m | returns, close | low-liquidity names with missing prints | Da, Gurun & Warachka 2014 |
| path efficiency | a smooth directional path (high signal-to-noise) is more likely to continue than a noisy path with the same endpoint | + | 1-3m | returns, close | regime transitions | — |

## 3. Liquidity and trading activity

| idea | mechanism | dir | horizon | fields | failure modes | origin |
|---|---|---|---|---|---|---|
| illiquidity premium | investors require compensation for holding names that are expensive to trade, so illiquid names carry higher expected returns | + | 1-6m | close, volume, amount | liquidity spirals; crowding | Amihud 2002 |
| abnormal activity level | unusually high dollar activity marks attention and temporary demand pressure | - | 3-10d | amount, adv20, volume | structural volume change; index events | Gervais, Kaniel & Mingelgrin 2001 |
| activity trend | a rising activity baseline signals accumulating institutional interest | + | 1-3m | volume, adv20, amount | retail mania; pump patterns | Chordia, Roll & Subrahmanyam 2001 |
| dollar-volume share shift | a name's share of market dollar volume drifting up marks rotation into it | + | 2-8w | amount, adv20 | market-wide volume shocks | — |
| activity concentration | activity clustered in few days (lumpiness) signals event risk rather than steady accumulation | - | 1-3m | volume, amount | genuine scheduled events | — |

## 4. Volatility, skewness and tails

| idea | mechanism | dir | horizon | fields | failure modes | origin |
|---|---|---|---|---|---|---|
| low-volatility anomaly | leverage-constrained and lottery-seeking investors overpay for high-volatility names, compressing their expected returns | - | 1-6m | returns, close | rising-rate/leverage unwinds | Ang et al. 2006 |
| maximum-return effect | a single extreme recent day attracts lottery demand and subsequent underperformance | - | 1-4w | returns, close | genuine rerating news | Bali, Cakici & Whitelaw 2011 |
| skewness preference | positively skewed payoff profiles are overpriced by lottery-seeking demand | - | 1-3m | returns, close | small-sample skew estimates | Boyer, Mitton & Vorkink 2010 |
| volatility-of-volatility | unstable second moments signal fragile liquidity provision and higher risk premia | - | 1-3m | returns, close | regime shifts; vol spikes | — |
| upside/downside volatility asymmetry | asymmetric responses reveal which side of the book is crowded | +/- | 1-3m | returns, close | structural breaks | — |

## 5. Price position and range geometry

| idea | mechanism | dir | horizon | fields | failure modes | origin |
|---|---|---|---|---|---|---|
| close position in range | closing near the high after a wide day reflects demand absorbed at the close; closing near the low reflects supply | + | 3-10d | high, low, close, range | thin prints; auction distortions | — |
| range compression | shrinking ranges signal consensus and coiled positioning; breakouts from compression carry information | + | 1-4w | high, low, range, close | false breakouts in low liquidity | — |
| range expansion exhaustion | unusually wide ranges mark climax behaviour that mean-reverts | - | 3-10d | high, low, range, close | real information shocks | — |
| location in multi-day range | where price sits in its own recent range captures relative value within the name's regime | - | 2-8w | high, low, close | trending regimes | — |
| close-to-high persistence | repeatedly closing near the high indicates persistent end-of-day demand | + | 1-3w | close, high, range | end-of-quarter window dressing | — |

## 6. Overnight and intraday channels

| idea | mechanism | dir | horizon | fields | failure modes | origin |
|---|---|---|---|---|---|---|
| overnight vs intraday split | institutions trade intraday, retail attention peaks overnight; the two return components carry opposite information | -/+ | 1-5d | overnight_return, intraday_return | macro overnight news | Lou, Polk & Skouras 2019 |
| open-gap continuation | gaps accompanied by broad participation continue rather than fade | + | 1-3d | open, close, volume | illiquid opens; auction noise | — |
| intraday range position at close | where the session closes tells whether the day's flow was absorbed | + | 3-10d | high, low, close | thin closing auctions | — |

## 7. Size and cross-sectional structure

| idea | mechanism | dir | horizon | fields | failure modes | origin |
|---|---|---|---|---|---|---|
| size premium | smaller names carry higher required returns and less coverage | - | 1-6m | cap, close | capacity constraints; liquidity spirals | Fama & French 1992 |
| size-conditioned reversal | reversal is stronger in less-covered, smaller names where liquidity provision is thinner | - | 3-10d | cap, close, volume | crowded small-cap flows | — |
| cross-sectional dispersion regime | when dispersion is high, stock-specific stories dominate and relative-value signals pay more | + | 1-3m | returns, cap | market-wide crashes | — |

## 8. Calendar and seasonality

| idea | mechanism | dir | horizon | fields | failure modes | origin |
|---|---|---|---|---|---|---|
| turn-of-month flow | payroll, rebalancing and window-dressing flows cluster around month boundaries | + | 1-5d | close, returns | calendar drift; regime changes | Ariel 1987 |
| day-of-week effect | participant mix varies by weekday, creating recurring demand imbalances | +/- | 1-5d | returns, close | weak under modern execution | French 1980 |
| holiday/short-week effect | pre-holiday positioning and thin liquidity create systematic drift | + | 1-5d | close, returns | small sample; unstable | — |

## How to use the catalogue

1. Pick **at most two rows from the same family** per batch; diversify across
   families, datasets and horizons.
2. Translate the row into the local situation: which universe, which liquidity,
   which horizon is plausible for the contracts you have.
3. State the mechanism in your own words for the exact universe; do not copy the
   row text.
4. Write the failure modes from the row plus one market-specific condition.
5. Record the origin only as evidence context; the idea must stand on its own.

## Origin references

Ariel 1987; Amihud 2002; Ang, Hodrick, Xing & Zhang 2006; Bali, Cakici &
Whitelaw 2011; Barber & Odean 2008; Berkman, Koch, Tuttle & Zhang 2012; Boyer,
Mitton & Vorkink 2010; Brock, Lakonishok & LeBaron 1992; Chordia, Roll &
Subrahmanyam 2001; Da, Gurun & Warachka 2014; Fama & French 1992; French 1980;
George & Hwang 2004; Gervais, Kaniel & Mingelgrin 2001; Heston, Korajczyk &
Sadka 2010; Jegadeesh 1990; Jegadeesh & Titman 1993; Lehmann 1990; Lou, Polk &
Skouras 2019; Moskowitz, Ooi & Pedersen 2012; Pastor & Stambaugh 2003.
