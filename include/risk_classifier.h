#ifndef PROJECT_BOOST_RISK_CLASSIFIER_H
#define PROJECT_BOOST_RISK_CLASSIFIER_H

namespace project_boost {

struct TransactionInput {
  int amount_cents;
  int failed_logins_last_24h;
  bool chargeback_last_30_days;
  bool account_age_under_30_days;
  bool manual_override;
};

enum class TransactionRisk {
  kRejected = 0,
  kLow = 1,
  kMedium = 2,
  kHigh = 3,
};

TransactionRisk ClassifyTransactionRisk(const TransactionInput& input);

}  // namespace project_boost

#endif
