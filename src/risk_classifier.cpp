#include "risk_classifier.h"

namespace project_boost {

TransactionRisk ClassifyTransactionRisk(const TransactionInput& input) {
  if (input.amount_cents <= 0) {
    return TransactionRisk::kRejected;
  }

  if (input.manual_override) {
    return TransactionRisk::kLow;
  }

  int risk_score = 0;

  if (input.amount_cents >= 250000) {
    risk_score += 4;
  } else if (input.amount_cents >= 100000) {
    risk_score += 2;
  } else if (input.amount_cents >= 30000) {
    risk_score += 1;
  }

  if (input.failed_logins_last_24h >= 5) {
    risk_score += 3;
  } else if (input.failed_logins_last_24h >= 2) {
    risk_score += 1;
  }

  if (input.chargeback_last_30_days) {
    risk_score += 3;
  }

  if (input.account_age_under_30_days) {
    risk_score += 2;
  }

  if (input.amount_cents >= 50000 &&
      input.failed_logins_last_24h == 0 &&
      !input.chargeback_last_30_days &&
      !input.account_age_under_30_days) {
    risk_score += 1;
  }

  if (risk_score >= 7) {
    return TransactionRisk::kHigh;
  }
  if (risk_score >= 3) {
    return TransactionRisk::kMedium;
  }
  return TransactionRisk::kLow;
}

}  // namespace project_boost
