# EDA Report — Montra Guest Experience Analytics


## 1. Data examined

| Table | Rows | Key content |
|---|---|---|
| reviews | 35,000 | review text, rating (1–5), review date, sentiment label |
| bookings | 35,000 | room type, channel, check-in/out, amount, stay length |
| guests | 12,000 | customer type, loyalty tier, country, previous stays |
| hotels | 25 | name, city (14), star rating, rooms |

All four tables were consolidated into one analytical table: 35,000 reviews × 22 columns, covering 11,377 guests from 2 January 2025 to 30 June 2026. Every review links to exactly one booking, guest and hotel. The joins lost or duplicated no rows.

## 2. Key findings

### Sentiment and ratings
- **The classes are balanced:** neutral 38.2%, positive 33.7%, negative 28.2%. Macro-averaged metrics are used so the smallest class counts equally.
- **Ratings centre on 3.0** (mean 3.03), with clear bands per label: negative ≈ 1.9, neutral ≈ 3.0, positive ≈ 4.0. The bands overlap, so ratings alone cannot reproduce the labels.
- **Label quality:** 94.65% of labels agree with their rating band. **1,871 reviews (5.35%) disagree**, and every disagreement sits on a neutral boundary; none jumps from positive to negative. This sets a practical ceiling of roughly 95% on achievable accuracy.

### Volume and time
- About **1,900–2,100 reviews a month**; January 2025 and June 2026 are partial months.
- The average rating stays between 2.97 and 3.06 and sentiment shares are flat across 18 months. There is no portfolio-wide trend or seasonality, so emerging issues have to be looked for per aspect and per hotel.

### Text characteristics
- Reviews are short and uniform: **13–40 words** (mean 29) and 2.5 sentences on average. 53% have two sentences and 41% have three.
- Length carries no sentiment signal (correlation with rating 0.002).
- **Each sentiment has its own vocabulary:**
  - negative: *disappointed, left a lot to be desired, sadly*
  - neutral: *fine, fairly ordinary, as expected*
  - positive: *genuinely impressed, exceeded expectations*
- **Negation** appears in 47.9% of negative reviews against 12.4% of positive ones. **Hedging** (*fine, acceptable*) appears in 81.9% of neutral reviews, but also in about 19% of positive and negative ones, which is why neutral is the hardest class.
- The text is **highly templated**: only 6,764 unique sentences across 85,829.

### Hotels
- The best and worst hotel average ratings differ by **0.56 points**.
- **Star rating is the strongest structured driver:** 3★ 2.86 → 4★ 3.09 → 5★ 3.33 (correlation +0.18).
- Nottingham (3.25) and London (3.24) lead. Edinburgh (2.84), Leicester, Oxford and Leeds trail, and every trailing city's hotels are 3★. Location and star level are confounded.

### Guests
- Customer type (3.00–3.06), loyalty tier (3.01–3.04), country (3.00–3.06) and repeat stays make almost no difference. The negative share stays at 27–29% in every segment.

### Bookings: satisfaction
- Room type, channel and stay length all sit within 3.01–3.05 average rating.
- Booking value is uncorrelated with satisfaction (r = +0.003). Paying more does not buy a better-rated stay.

### Bookings: commercial view (extending `data_extraction.ipynb`)

| Total revenue £16.31m | Share of bookings | Share of revenue | Average booking value |
|---|---|---|---|
| Deluxe | 24.6% | 24.1% | £457 |
| Standard | 30.3% | 19.1% | £294 |
| Suite | 10.1% | 18.6% | £855 |
| Executive | 15.1% | 19.7% | £607 |
| Family Room | 11.8% | 13.2% | £522 |
| Twin | 8.0% | 5.3% | £306 |

- **Channel revenue mirrors channel volume:** average booking value is £459–472 on every channel. Direct Website (24.8%) and Booking.com (22.4%) together bring in almost half of revenue; the three online travel agents (Booking.com, Expedia, Airbnb) bring in 47%.
- **Stays:** 2 nights is the most common (29.8%); the median is 3. **No booking lasts 6 nights**, although 7-night stays exist. This gap should be confirmed with the data owner.
- Revenue mix and satisfaction are decoupled. The highest-value rooms (Suites) are rated no better than the cheapest.

## 3. Data quality observations carried into cleaning

| Issue | Scale | Treatment (Phase 4) |
|---|---|---|
| `loyalty_status` missing | 6,036 guests (17,615 review rows) | Structural (not enrolled) → *No membership* |
| Identical review text | 829 reviews in 365 groups | Kept for analytics; de-duplicated for modelling to avoid leakage |
| Same text, conflicting labels | 76 groups, 196 reviews | Excluded from the modelling corpus |
| Two hotels share one name | *Edinburgh Riverside Hotel* #9 and #14 | Disambiguated |
| Typographic characters | 12,398 reviews | Unicode-normalised |
| Labels contradicting ratings | 1,871 reviews (5.35%) | Flagged (`label_rating_conflict`) for error analysis |

No invalid ratings, missing identifiers or inconsistent dates were found. Every review is posted 0–14 days after check-out.

## 4. Implications for modelling

1. **Model at sentence level.** Most reviews discuss two or three aspects, so topics and aspect sentiment are measured per sentence.
2. **Keep negation** in preprocessing; it is a genuine signal.
3. **Use macro-F1**, expect *neutral* to be the hardest class, and treat about 95% as the realistic ceiling because of label noise.
4. **Look to the text, not the structured data.** Structured variables explain almost nothing about satisfaction; only hotel and star rating matter.
