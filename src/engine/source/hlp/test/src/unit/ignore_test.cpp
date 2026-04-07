#include <gtest/gtest.h>

#include "hlp_test.hpp"

auto constexpr NAME = "ignoreParser";

INSTANTIATE_TEST_SUITE_P(IgnoreBuild,
                         HlpBuildTest,
                         ::testing::Values(BuildT(FAILURE, getIgnoreParser, {NAME, "", {}, {}}),
                                           BuildT(SUCCESS, getIgnoreParser, {NAME, "", {}, {"ignore"}}),
                                           BuildT(FAILURE, getIgnoreParser, {NAME, "", {}, {"ignore", "unexpected"}}),
                                           BuildT(FAILURE, getIgnoreParser, {NAME, "not allow", {}, {"ignore"}})));

INSTANTIATE_TEST_SUITE_P(
    IgnoreParse,
    HlpParseTest,
    ::testing::Values(ParseT(SUCCESS, "assetguard", j("{}"), 5, getIgnoreParser, {NAME, "", {}, {"assetguard"}}),
                      ParseT(SUCCESS, "assetguard 123", j("{}"), 5, getIgnoreParser, {NAME, "", {}, {"assetguard"}}),
                      ParseT(SUCCESS, "assetguardassetguard", j("{}"), 10, getIgnoreParser, {NAME, "", {}, {"assetguard"}}),
                      ParseT(SUCCESS, "assetguardassetguardassetguardassetguard", j("{}"), 20, getIgnoreParser, {NAME, "", {}, {"assetguard"}}),
                      ParseT(SUCCESS, "assetguardwa", j("{}"), 5, getIgnoreParser, {NAME, "", {}, {"assetguard"}}),
                      ParseT(FAILURE, "ASSETGUARD", j("{}"), 0, getIgnoreParser, {NAME, "", {}, {"assetguard"}})));
