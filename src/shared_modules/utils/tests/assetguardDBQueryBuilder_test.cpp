/*
 * AssetGuard shared modules utils
 * Copyright (C) 2015, AssetGuard Inc.
 * Nov 1, 2023.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation.
 */

#include "assetguardDBQueryBuilder_test.hpp"
#include "assetguardDBQueryBuilder.hpp"
#include <string>

TEST_F(AssetGuardDBQueryBuilderTest, GlobalTest)
{
    std::string message = AssetGuardDBQueryBuilder::builder().global().selectAll().fromTable("agent").build();
    EXPECT_EQ(message, "global sql SELECT * FROM agent ");
}

TEST_F(AssetGuardDBQueryBuilderTest, AgentTest)
{
    std::string message = AssetGuardDBQueryBuilder::builder().agent("0").selectAll().fromTable("sys_programs").build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs ");
}

TEST_F(AssetGuardDBQueryBuilderTest, WhereTest)
{
    std::string message = AssetGuardDBQueryBuilder::builder()
                              .agent("0")
                              .selectAll()
                              .fromTable("sys_programs")
                              .whereColumn("name")
                              .equalsTo("bash")
                              .build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs WHERE name = 'bash' ");
}

TEST_F(AssetGuardDBQueryBuilderTest, WhereAndTest)
{
    std::string message = AssetGuardDBQueryBuilder::builder()
                              .agent("0")
                              .selectAll()
                              .fromTable("sys_programs")
                              .whereColumn("name")
                              .equalsTo("bash")
                              .andColumn("version")
                              .equalsTo("1")
                              .build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs WHERE name = 'bash' AND version = '1' ");
}

TEST_F(AssetGuardDBQueryBuilderTest, WhereOrTest)
{
    std::string message = AssetGuardDBQueryBuilder::builder()
                              .agent("0")
                              .selectAll()
                              .fromTable("sys_programs")
                              .whereColumn("name")
                              .equalsTo("bash")
                              .orColumn("version")
                              .equalsTo("1")
                              .build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs WHERE name = 'bash' OR version = '1' ");
}

TEST_F(AssetGuardDBQueryBuilderTest, WhereIsNullTest)
{
    std::string message = AssetGuardDBQueryBuilder::builder()
                              .agent("0")
                              .selectAll()
                              .fromTable("sys_programs")
                              .whereColumn("name")
                              .isNull()
                              .build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs WHERE name IS NULL ");
}

TEST_F(AssetGuardDBQueryBuilderTest, WhereIsNotNullTest)
{
    std::string message = AssetGuardDBQueryBuilder::builder()
                              .agent("0")
                              .selectAll()
                              .fromTable("sys_programs")
                              .whereColumn("name")
                              .isNotNull()
                              .build();
    EXPECT_EQ(message, "agent 0 sql SELECT * FROM sys_programs WHERE name IS NOT NULL ");
}

TEST_F(AssetGuardDBQueryBuilderTest, InvalidValue)
{
    EXPECT_THROW(AssetGuardDBQueryBuilder::builder()
                     .agent("0")
                     .selectAll()
                     .fromTable("sys_programs")
                     .whereColumn("name")
                     .equalsTo("bash'")
                     .build(),
                 std::runtime_error);
}

TEST_F(AssetGuardDBQueryBuilderTest, InvalidColumn)
{
    EXPECT_THROW(AssetGuardDBQueryBuilder::builder()
                     .agent("0")
                     .selectAll()
                     .fromTable("sys_programs")
                     .whereColumn("name'")
                     .equalsTo("bash")
                     .build(),
                 std::runtime_error);
}

TEST_F(AssetGuardDBQueryBuilderTest, InvalidTable)
{
    EXPECT_THROW(AssetGuardDBQueryBuilder::builder()
                     .agent("0")
                     .selectAll()
                     .fromTable("sys_programs'")
                     .whereColumn("name")
                     .equalsTo("bash")
                     .build(),
                 std::runtime_error);
}

TEST_F(AssetGuardDBQueryBuilderTest, GlobalGetCommand)
{
    std::string message = AssetGuardDBQueryBuilder::builder().globalGetCommand("agent-info 1").build();
    EXPECT_EQ(message, "global get-agent-info 1 ");
}

TEST_F(AssetGuardDBQueryBuilderTest, GlobalFindCommand)
{
    std::string message = AssetGuardDBQueryBuilder::builder().globalFindCommand("agent 1").build();
    EXPECT_EQ(message, "global find-agent 1 ");
}

TEST_F(AssetGuardDBQueryBuilderTest, GlobalSelectCommand)
{
    std::string message = AssetGuardDBQueryBuilder::builder().globalSelectCommand("agent-name 1").build();
    EXPECT_EQ(message, "global select-agent-name 1 ");
}

TEST_F(AssetGuardDBQueryBuilderTest, AgentGetOsInfoCommand)
{
    std::string message = AssetGuardDBQueryBuilder::builder().agentGetOsInfoCommand("1").build();
    EXPECT_EQ(message, "agent 1 osinfo get ");
}

TEST_F(AssetGuardDBQueryBuilderTest, AgentGetHotfixesCommand)
{
    std::string message = AssetGuardDBQueryBuilder::builder().agentGetHotfixesCommand("1").build();
    EXPECT_EQ(message, "agent 1 hotfix get ");
}

TEST_F(AssetGuardDBQueryBuilderTest, AgentGetPackagesCommand)
{
    std::string message = AssetGuardDBQueryBuilder::builder().agentGetPackagesCommand("1").build();
    EXPECT_EQ(message, "agent 1 package get ");
}
