# Evaluation contract

- Split complete events 70% train, 15% calibration, 15% test without shuffling.
- Require prior-block settlement before later-block prediction.
- Fit TF-IDF and classifier on train only; fit Platt calibration on calibration only.
- Compare identical model families under safe as-of filtering and an explicitly leaky all-revision join.
- Report discrimination and calibration together; never promote the leaky path.
