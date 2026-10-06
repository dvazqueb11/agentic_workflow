#include "risk_classifier.h"

#include <gtest/gtest.h>

namespace {

using project_boost::ClassifyTransactionRisk;
using project_boost::TransactionInput;
using project_boost::TransactionRisk;

TEST(RiskClassifierTest, RejectsNonPositiveAmount) {
  const TransactionInput input{
      0,
      0,
      false,
      false,
      false,
  };
  EXPECT_EQ(ClassifyTransactionRisk(input), TransactionRisk::kRejected);
}

TEST(RiskClassifierTest, HonorsManualOverride) {
  const TransactionInput input{
      900000,
      8,
      true,
      true,
      true,
  };
  EXPECT_EQ(ClassifyTransactionRisk(input), TransactionRisk::kLow);
}

TEST(RiskClassifierTest, ClassifiesMediumRiskFromAmountAndRecentLogins) {
  const TransactionInput input{
      110000,
      2,
      false,
      false,
      false,
  };
  EXPECT_EQ(ClassifyTransactionRisk(input), TransactionRisk::kMedium);
}

TEST(RiskClassifierTest, ClassifiesHighRiskFromCombinedSignals) {
  const TransactionInput input{
      250000,
      5,
      false,
      false,
      false,
  };
  EXPECT_EQ(ClassifyTransactionRisk(input), TransactionRisk::kHigh);
}

TEST(RiskClassifierTest, ClassifiesLowRiskWithoutRiskSignals) {
  const TransactionInput input{
      1500,
      1,
      false,
      false,
      false,
  };
  EXPECT_EQ(ClassifyTransactionRisk(input), TransactionRisk::kLow);
}

TEST(RiskClassifierTest, ClassifiesMediumRiskForChargebackAndYoungAccount) {
  const TransactionInput input{
      25000,
      0,
      true,
      true,
      false,
  };
  EXPECT_EQ(ClassifyTransactionRisk(input), TransactionRisk::kMedium);
}

TEST(RiskClassifierTest, ClassifiesLowRiskForModerateAmountBelowBonusThreshold) {
  const TransactionInput input{
      40000,
      0,
      false,
      false,
      false,
  };
  EXPECT_EQ(ClassifyTransactionRisk(input), TransactionRisk::kLow);
}

TEST(RiskClassifierTest, ClassifiesMediumRiskWhenCleanSignalBonusReachesThreshold) {
  const TransactionInput input{
      100000,
      1,
      false,
      false,
      false,
  };
  EXPECT_EQ(ClassifyTransactionRisk(input), TransactionRisk::kMedium);
}

TEST(RiskClassifierTest, SkipsCleanSignalBonusWhenRecentFailedLoginsExist) {
  const TransactionInput input{
      60000,
      2,
      false,
      false,
      false,
  };
  EXPECT_EQ(ClassifyTransactionRisk(input), TransactionRisk::kLow);
}

}  // namespace
