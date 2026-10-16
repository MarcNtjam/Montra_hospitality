# Business Insight Report — Montra Guest Experience Analytics

**Phase 9** · Source: `notebook/guest_experience_analysis.ipynb`, Phases 6 and 9 · Data: 35,000 reviews, 25 hotels in 14 UK cities, January 2025 – June 2026


## Key findings

**1. Ratings show how guests feel; the text shows why.** Booking value, room type, channel, stay length and guest profile explain essentially nothing about satisfaction (all correlations ≈ 0). Aspect-level sentiment extracted from the text explains **74%** of the variation in ratings.

**2. Satisfaction is decided at property level.** Hotels differ by **41.5 points** of net sentiment; customer segments by under 4. Star rating is the strongest structured driver (3★ 2.86 → 5★ 3.33 average rating), and all six weakest hotels are 3★.

**3. Every weak hotel has its own problem.** Across the portfolio the seven aspects are within 2.5 points of each other, so there is no single "worst aspect" to fix everywhere. At hotel level the gaps are large and specific: value at Edinburgh Riverside #14 and Glasgow Harbour, staff at Edinburgh Riverside #9, food at Glasgow Skyline, cleanliness and room condition at The Glasgow Heritage, location and room condition at The Oxford Boutique.

**4. Value for money is the most common weak spot.** Pricing & Value has the most negative mentions (2,029), the highest rating impact per mention (0.51) and the most repeated complaints. The complaint is specific: **extras charged on top of the rate** and **quality not matching the price**.

**5. Neutral is the biggest opportunity.** About half of all aspect mentions are neutral (*"fine"*, *"adequate"*). Most guests are not unhappy; they are unimpressed.

## Recommendations

| Priority | Recommendation | Evidence | Where |
|---|---|---|---|
| 1 | Review rate transparency: bundle or clearly disclose extras at booking | Pricing & Value: most complaints (2,029) and highest rating impact; the most repeated complaint sentences cite extras and value | All hotels, starting with Edinburgh Riverside #14 and #9 and Glasgow Harbour |
| 2 | Run a full operational review of the two Edinburgh Riverside hotels | Lowest net sentiment in the portfolio (−9.2 and −9.1); five of the ten largest hotel × aspect gaps (value, food, location, staff) | Edinburgh Riverside #9 and #14 |
| 3 | Targeted housekeeping and maintenance audits | Cleanliness & Room Condition 15–17 pts below portfolio; complaints about unscrubbed bathrooms and rooms not cleaned that day | The Glasgow Heritage, The Oxford Boutique |
| 4 | Review food quality and menu rotation | Food & Dining 14–15 pts below portfolio; complaints about reheated items and the same dishes every day | Glasgow Skyline, Edinburgh Riverside #14 |
| 5 | Peak-time front-desk staffing and check-in system reliability | Check-in complaints: system crashes, rooms not ready on arrival | Portfolio-wide, starting with The Brighton Heritage (−14 pts on check-in) |
| 6 | Manage location expectations (transport guidance, evening information, shuttle options in listings) | Location & Transport is the only aspect trending worse; complaints about access without a car and little to do after dark | The Oxford Boutique, Edinburgh Riverside #9 |
| 7 | Copy what the best hotels do | Nottingham Riverside is praised for value (+15.9 pts above portfolio), The London Heritage for check-in (+15.4) and Liverpool Metropolitan for location (+13.6) | Pair each weak hotel with a strong one on its signature complaint, e.g. Edinburgh Riverside #14 with Nottingham Riverside on value |
| 8 | Benchmark hotels within their star tier | Star rating sets the baseline; a 3★ hotel at 2.9 may be performing to standard | Reporting |
| 9 | Use the classifier for automated tagging, with a monthly hotel × aspect report | 94% accurate; outputs keyed by `review_id` with model version | Montra platform |
| 10 | Audit labelling: re-label the ~5% of reviews whose label contradicts the rating | 89% of model errors trace to these | Data team |

## Limitations

- **Templated text.** The review text is highly templated (only 6,764 unique sentences). Real guest language will be more varied, so performance should be re-validated on live reviews before use.
- **Offline model choices in this execution.** Hugging Face was unreachable, so topic embeddings used RoBERTa-base (layers 4–8, aspect-focused) instead of `all-MiniLM-L6-v2`, and the RoBERTa weights came from spaCy's `en_core_web_trf` release (see the README). With internet access the notebook uses the original models.
- **No mixed reviews.** No review combines strong praise with a strong complaint, so true mixed-sentiment handling is untested.
- **Untested scope.** Only English reviews were analysed, and sarcasm and emotion were out of scope.

## The evidence in numbers

### Hotels: where satisfaction is won and lost

| Weakest hotels (all 3★) | Net sentiment | Signature complaint |
|---|---|---|
| Edinburgh Riverside #14 | −9.2 | Pricing & Value |
| Edinburgh Riverside #9 | −9.1 | Staff & Service |
| Glasgow Skyline | −8.9 | Food & Dining |
| Glasgow Harbour | −8.3 | Pricing & Value |
| The Glasgow Heritage | −7.4 | Cleanliness & Room Condition |
| The Oxford Boutique | −7.0 | Location & Transport |

| Strongest hotels | Net sentiment | Signature strength (praise rate above portfolio) |
|---|---|---|
| Nottingham Riverside | +32.2 | Pricing & Value (+15.9 pts), Check-in & Arrival (+14.4), Facilities (+13.5) |
| The London Heritage | +28.0 | Check-in & Arrival (+15.4), Cleanliness & Room Condition (+13.6) |
| Liverpool Metropolitan | +25.4 | Location & Transport (+13.6) |

- Net sentiment = % positive − % negative reviews (predicted by the model). It tracks average rating almost perfectly (r = 0.998).
- By city, Edinburgh (−9.1) and Oxford (−7.0) trail; Nottingham (+21.1) and London (+20.6) lead.
- Guest segments barely differ: customer type, loyalty tier, booking channel and room type each span under 4 points (families +7.4, groups +3.7).

### Aspects: portfolio view

| Aspect | Mentions | Negative | Positive | Net | Rating impact per mention |
|---|---|---|---|---|---|
| Pricing & Value | 8,615 | 23.6% | 26.3% | +2.8 | 0.510 |
| Staff & Service | 8,582 | 23.0% | 26.8% | +3.8 | 0.460 |
| Location & Transport | 8,431 | 23.4% | 27.2% | +3.8 | 0.484 |
| Check-in & Arrival | 8,801 | 22.3% | 26.1% | +3.8 | 0.477 |
| Food & Dining | 8,769 | 21.6% | 26.2% | +4.6 | 0.454 |
| Facilities | 8,743 | 22.2% | 26.9% | +4.8 | 0.444 |
| Cleanliness & Room Condition | 8,625 | 22.6% | 27.8% | +5.3 | 0.452 |

All seven aspects are close at portfolio level; the large gaps appear hotel by hotel (up to 17 points below the portfolio on a single aspect).

### What guests actually say

| Aspect | Most repeated complaints |
|---|---|
| Pricing & Value | *"several amenities cost extra on top of the rate"*, *"the quality didn't match the price tag"*, *"we found better options nearby for less"* |
| Location & Transport | *"hard to reach without a car"*, *"very little around after dark"*, *"a rather unsafe area"* |
| Staff & Service | *"our complaints were largely ignored"*, *"communication was a constant struggle"*, *"we had to ask twice"* |
| Check-in & Arrival | *"the system apparently crashed while we waited"*, *"our room wasn't ready despite an on-time arrival"* |
| Cleanliness & Room Condition | *"the bathroom hadn't been properly scrubbed"*, *"it clearly hadn't been cleaned that day"* |
| Facilities | *"needed a serious refurbishment"*, *"parts of it weren't working properly"* |
| Food & Dining | *"several items were clearly reheated"*, *"the same few dishes appeared every single day"* |

The most repeated praise is about **location** (*"ideally situated"*, *"perfectly placed for exploring"*) and **value** (*"excellent value"*, *"a great deal"*).

### Trends

Over 18 months no aspect's negative share moved by more than 2.6 points. **Location & Transport is the only aspect drifting worse (+0.8 pts)**; Cleanliness & Room Condition improved the most (−2.6 pts).

## How these results were produced

Reviews were split into 85,829 sentences. BERTopic grouped them into 29 topics, which were mapped to seven business aspects and checked sentence by sentence. Each sentence was scored positive, neutral or negative by a domain-trained classifier (0.909 macro-F1 at sentence level, against 0.596 for the general-purpose VADER lexicon). Each review was scored by the selected sentiment model (Random Forest, 0.942 test macro-F1). Outputs are stored in `data/processed/review_model_outputs.csv`, linked to the source data by `review_id`, with the model version on every row.
