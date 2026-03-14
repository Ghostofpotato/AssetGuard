# Find the assetguard shared library
find_library(
  ASSETGUARDLIB
  NAMES libassetguard_test.a
  HINTS "${SRC_FOLDER}/build/lib")
find_library(
  ASSETGUARDEXT
  NAMES libassetguardext.so
  HINTS "${SRC_FOLDER}/build/lib")
set(uname "Linux")

if(NOT ASSETGUARDLIB)
  message(FATAL_ERROR "libassetguard_test.a not found in ${SRC_FOLDER}/build/lib! Aborting...")
endif()

if(NOT ASSETGUARDEXT)
  message(FATAL_ERROR "libassetguardext not found in ${SRC_FOLDER}/build/lib! Aborting...")
endif()

# Add compiling flags
add_compile_options(
  -ggdb
  -O0
  -g
  -coverage
  -DTEST_SERVER
  -DENABLE_AUDIT
  -DINOTIFY_ENABLED
  -fsanitize=address
  -fsanitize=undefined)
link_libraries(-fsanitize=address -fsanitize=undefined)

# Set tests dependencies - use linker groups to resolve circular dependencies
link_directories("${SRC_FOLDER}/build/lib/")
set(TEST_DEPS
    -Wl,--start-group
    ${ASSETGUARDLIB}
    ${ASSETGUARDEXT}
    -lrouter
    -lschema_validator
    -Wl,--end-group
    -lpthread
    -ldl
    -lcmocka
    -fprofile-arcs
    -ftest-coverage)

add_subdirectory(remoted)
add_subdirectory(assetguard_db)
add_subdirectory(os_auth)
add_subdirectory(os_crypto)
add_subdirectory(assetguard_modules)
add_subdirectory(monitord)
