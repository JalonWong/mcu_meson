#include <gtest/gtest.h>

#include "lib.h"

TEST(MY_TEST, TEST1) {
    ASSERT_EQ(1, 1);
    ASSERT_EQ(get_lib_version(), 9);
}
