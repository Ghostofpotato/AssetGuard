cmake_minimum_required(VERSION 3.12.4)

project(assetguard C)

if(NOT DEFINED ASSETGUARD_MAIN_PROJECT)
  get_filename_component(SRC_FOLDER ${CMAKE_SOURCE_DIR}/../ ABSOLUTE)
endif()

# Include directories
include_directories(
  ${SRC_FOLDER}/external/audit-userspace/lib
  ${SRC_FOLDER}/external/curl/include/curl/
  ${SRC_FOLDER}/external/libpcre2/include/
  ${SRC_FOLDER}/external/sqlite/
  ${SRC_FOLDER}/external/libyaml/include
  ${SRC_FOLDER}/external/libplist/bin/include/
  ${SRC_FOLDER}/external/bzip2/
  ${SRC_FOLDER}/external/zlib/
  ${SRC_FOLDER}/active-response/include
  ${SRC_FOLDER}/client-agent/include
  ${SRC_FOLDER}/config/include
  ${SRC_FOLDER}/logcollector/include
  ${SRC_FOLDER}/os_auth/include
  ${SRC_FOLDER}/shared_modules/dbsync/include
  ${SRC_FOLDER}/syscheckd/include
  ${SRC_FOLDER}/data_provider/include
  ${SRC_FOLDER}/assetguard_modules/include
  ${SRC_FOLDER}/assetguard_modules/src
  ${SRC_FOLDER}/assetguard_modules/src/agent_upgrade
  ${SRC_FOLDER}/assetguard_modules/src/agent_upgrade/agent
  ${SRC_FOLDER}/assetguard_modules/src/agent_upgrade/manager
  ${SRC_FOLDER}/assetguard_modules/src/task_manager
  ${SRC_FOLDER}/assetguard_db/include
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/include/error_messages
  ${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/md5
  ${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/sha1
  ${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/sha256
  ${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/md5_sha1_sha256
  ${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/blowfish
  ${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/sha512
  ${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/aes
  ${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/hmac
  ${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/shared
  ${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/signature
  ${CMAKE_CURRENT_SOURCE_DIR}/os_net
  ${CMAKE_CURRENT_SOURCE_DIR}/os_regex
  ${CMAKE_CURRENT_SOURCE_DIR}/os_xml
  ${CMAKE_CURRENT_SOURCE_DIR}/os_zlib)

if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
  add_definitions(-DWIN32=1 -D_POSIX_C_SOURCE -DPSAPI_VERSION=1)
elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
  add_definitions(-DDarwin -DHIGHFIRST)
endif()

# Collect all source files from the various subdirectories
file(GLOB SHARED_CORE_SRC "${CMAKE_CURRENT_SOURCE_DIR}/src/*.c")

# Remove server-only files that use features not available on Windows
if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
  list(
    REMOVE_ITEM
    SHARED_CORE_SRC
    "${CMAKE_CURRENT_SOURCE_DIR}/src/batch_queue_op.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/http_op.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/indexed_queue_op.c")
endif()
file(GLOB OS_CRYPTO_BLOWFISH_SRC
     "${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/blowfish/*.c")
file(GLOB OS_CRYPTO_MD5_SRC "${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/md5/*.c")
file(GLOB OS_CRYPTO_SHA1_SRC "${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/sha1/*.c")
file(GLOB OS_CRYPTO_SHA256_SRC
     "${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/sha256/*.c")
file(GLOB OS_CRYPTO_SHA512_SRC
     "${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/sha512/*.c")
file(GLOB OS_CRYPTO_AES_SRC "${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/aes/*.c")
file(GLOB OS_CRYPTO_MD5_SHA1_SHA256_SRC
     "${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/md5_sha1_sha256/*.c")
file(GLOB OS_CRYPTO_HMAC_SRC "${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/hmac/*.c")
file(GLOB OS_CRYPTO_SHARED_SRC
     "${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/shared/*.c")
file(GLOB OS_CRYPTO_SIGNATURE_SRC
     "${CMAKE_CURRENT_SOURCE_DIR}/os_crypto/signature/*.c")
file(GLOB OS_NET_SRC "${CMAKE_CURRENT_SOURCE_DIR}/os_net/*.c")
file(GLOB OS_REGEX_SRC "${CMAKE_CURRENT_SOURCE_DIR}/os_regex/*.c")
file(GLOB OS_XML_SRC "${CMAKE_CURRENT_SOURCE_DIR}/os_xml/*.c")
file(GLOB OS_ZLIB_SRC "${CMAKE_CURRENT_SOURCE_DIR}/os_zlib/*.c")

# Active response shared utilities (used by execd and active response binaries)
set(ACTIVE_RESPONSE_SRC "${SRC_FOLDER}/active-response/src/active_responses.c")

# Combine all sources
set(LIBASSETGUARD_SRC
    ${SHARED_CORE_SRC}
    ${OS_CRYPTO_BLOWFISH_SRC}
    ${OS_CRYPTO_MD5_SRC}
    ${OS_CRYPTO_SHA1_SRC}
    ${OS_CRYPTO_SHA256_SRC}
    ${OS_CRYPTO_SHA512_SRC}
    ${OS_CRYPTO_AES_SRC}
    ${OS_CRYPTO_MD5_SHA1_SHA256_SRC}
    ${OS_CRYPTO_HMAC_SRC}
    ${OS_CRYPTO_SHARED_SRC}
    ${OS_CRYPTO_SIGNATURE_SRC}
    ${OS_NET_SRC}
    ${OS_REGEX_SRC}
    ${OS_XML_SRC}
    ${OS_ZLIB_SRC}
    ${ACTIVE_RESPONSE_SRC})

# Add unit test wrappers if UNIT_TEST is enabled
if(UNIT_TEST)
  # Collect wrapper source files
  file(GLOB WRAPPERS_COMMON_SRC "${SRC_FOLDER}/unit_tests/wrappers/*.c")
  file(GLOB WRAPPERS_EXTERNALS_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/externals/*.c")
  file(GLOB WRAPPERS_EXTERNALS_BZIP2_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/externals/bzip2/*.c")
  file(GLOB WRAPPERS_EXTERNALS_ZLIB_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/externals/zlib/*.c")
  file(GLOB WRAPPERS_EXTERNALS_CJSON_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/externals/cJSON/*.c")
  file(GLOB WRAPPERS_EXTERNALS_OPENSSL_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/externals/openssl/*.c")
  file(GLOB WRAPPERS_EXTERNALS_SQLITE_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/externals/sqlite/*.c")
  file(GLOB WRAPPERS_EXTERNALS_PCRE2_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/externals/pcre2/*.c")
  file(GLOB WRAPPERS_LIBC_SRC "${SRC_FOLDER}/unit_tests/wrappers/libc/*.c")
  file(GLOB WRAPPERS_POSIX_SRC "${SRC_FOLDER}/unit_tests/wrappers/posix/*.c")
  file(GLOB WRAPPERS_ASSETGUARD_SRC "${SRC_FOLDER}/unit_tests/wrappers/assetguard/*.c")
  file(GLOB WRAPPERS_ASSETGUARD_OS_CRYPTO_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/os_crypto/*.c")
  file(GLOB WRAPPERS_ASSETGUARD_OS_EXECD_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/os_execd/*.c")
  file(GLOB WRAPPERS_ASSETGUARD_OS_NET_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/os_net/*.c")
  file(GLOB WRAPPERS_ASSETGUARD_OS_REGEX_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/os_regex/*.c")
  file(GLOB WRAPPERS_ASSETGUARD_OS_XML_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/os_xml/*.c")
  file(GLOB WRAPPERS_ASSETGUARD_SHARED_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/shared/*.c")
  file(GLOB WRAPPERS_ASSETGUARD_SYSCHECKD_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/syscheckd/*.c")
  file(GLOB WRAPPERS_ASSETGUARD_ASSETGUARD_DB_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/assetguard_db/*.c")
  file(GLOB WRAPPERS_ASSETGUARD_ASSETGUARD_MODULES_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/assetguard_modules/*.c")
  if(IS_AGENT)
    list(
      REMOVE_ITEM
      WRAPPERS_ASSETGUARD_ASSETGUARD_MODULES_SRC
      "${SRC_FOLDER}/unit_tests/wrappers/assetguard/assetguard_modules/wm_task_manager_wrappers.c"
    )
  endif()
  file(GLOB WRAPPERS_ASSETGUARD_MONITORD_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/monitord/*.c")
  file(GLOB WRAPPERS_ASSETGUARD_OS_AUTH_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/os_auth/*.c")
  file(GLOB WRAPPERS_ASSETGUARD_ADDAGENT_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/addagent/*.c")
  file(GLOB WRAPPERS_ASSETGUARD_CONFIG_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/config/*.c")
  file(GLOB WRAPPERS_CLIENT_AGENT_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/client-agent/*.c")
  file(GLOB WRAPPERS_ASSETGUARD_REMOTED_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/remoted/*.c")
  file(GLOB WRAPPERS_DATA_PROVIDER_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/data_provider/*.c")
  file(GLOB WRAPPERS_LOGCOLLECTOR_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/logcollector/*.c")
  file(GLOB WRAPPERS_SHARED_MODULES_SRC
       "${SRC_FOLDER}/unit_tests/wrappers/assetguard/shared_modules/*.c")

  # Platform-specific wrappers configuration
  if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    # Windows uses its own wrapper implementations
    file(GLOB WRAPPERS_WINDOWS_SRC
         "${SRC_FOLDER}/unit_tests/wrappers/windows/*.c")
    file(GLOB WRAPPERS_WINDOWS_LIBC_SRC
         "${SRC_FOLDER}/unit_tests/wrappers/windows/libc/*.c")
    file(GLOB WRAPPERS_WINDOWS_POSIX_SRC
         "${SRC_FOLDER}/unit_tests/wrappers/windows/posix/*.c")

    set(UNIT_TEST_WRAPPERS_SRC
        ${WRAPPERS_COMMON_SRC}
        ${WRAPPERS_EXTERNALS_SRC}
        ${WRAPPERS_EXTERNALS_BZIP2_SRC}
        ${WRAPPERS_EXTERNALS_ZLIB_SRC}
        ${WRAPPERS_EXTERNALS_CJSON_SRC}
        ${WRAPPERS_EXTERNALS_OPENSSL_SRC}
        ${WRAPPERS_EXTERNALS_SQLITE_SRC}
        ${WRAPPERS_EXTERNALS_PCRE2_SRC}
        ${WRAPPERS_LIBC_SRC}
        ${WRAPPERS_POSIX_SRC}
        ${WRAPPERS_ASSETGUARD_SRC}
        ${WRAPPERS_ASSETGUARD_OS_CRYPTO_SRC}
        ${WRAPPERS_ASSETGUARD_OS_EXECD_SRC}
        ${WRAPPERS_ASSETGUARD_OS_NET_SRC}
        ${WRAPPERS_ASSETGUARD_OS_REGEX_SRC}
        ${WRAPPERS_ASSETGUARD_OS_XML_SRC}
        ${WRAPPERS_ASSETGUARD_SHARED_SRC}
        ${WRAPPERS_ASSETGUARD_SYSCHECKD_SRC}
        ${WRAPPERS_ASSETGUARD_ASSETGUARD_DB_SRC}
        ${WRAPPERS_ASSETGUARD_ASSETGUARD_MODULES_SRC}
        ${WRAPPERS_ASSETGUARD_MONITORD_SRC}
        ${WRAPPERS_ASSETGUARD_OS_AUTH_SRC}
        ${WRAPPERS_ASSETGUARD_ADDAGENT_SRC}
        ${WRAPPERS_ASSETGUARD_CONFIG_SRC}
        ${WRAPPERS_CLIENT_AGENT_SRC}
        ${WRAPPERS_ASSETGUARD_REMOTED_SRC}
        ${WRAPPERS_DATA_PROVIDER_SRC}
        ${WRAPPERS_LOGCOLLECTOR_SRC}
        ${WRAPPERS_SHARED_MODULES_SRC}
        ${WRAPPERS_WINDOWS_SRC}
        ${WRAPPERS_WINDOWS_LIBC_SRC}
        ${WRAPPERS_WINDOWS_POSIX_SRC})

  elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
    # macOS uses POSIX wrappers with --wrap linker flag
    file(GLOB WRAPPERS_MACOS_SRC "${SRC_FOLDER}/unit_tests/wrappers/macos/*.c")
    file(GLOB WRAPPERS_MACOS_LIBC_SRC
         "${SRC_FOLDER}/unit_tests/wrappers/macos/libc/*.c")
    file(GLOB WRAPPERS_MACOS_POSIX_SRC
         "${SRC_FOLDER}/unit_tests/wrappers/macos/posix/*.c")

    set(UNIT_TEST_WRAPPERS_SRC
        ${WRAPPERS_COMMON_SRC}
        ${WRAPPERS_EXTERNALS_SRC}
        ${WRAPPERS_EXTERNALS_BZIP2_SRC}
        ${WRAPPERS_EXTERNALS_ZLIB_SRC}
        ${WRAPPERS_EXTERNALS_CJSON_SRC}
        ${WRAPPERS_EXTERNALS_OPENSSL_SRC}
        ${WRAPPERS_EXTERNALS_SQLITE_SRC}
        ${WRAPPERS_EXTERNALS_PCRE2_SRC}
        ${WRAPPERS_LIBC_SRC}
        ${WRAPPERS_POSIX_SRC}
        ${WRAPPERS_ASSETGUARD_SRC}
        ${WRAPPERS_ASSETGUARD_OS_CRYPTO_SRC}
        ${WRAPPERS_ASSETGUARD_OS_EXECD_SRC}
        ${WRAPPERS_ASSETGUARD_OS_NET_SRC}
        ${WRAPPERS_ASSETGUARD_OS_REGEX_SRC}
        ${WRAPPERS_ASSETGUARD_OS_XML_SRC}
        ${WRAPPERS_ASSETGUARD_SHARED_SRC}
        ${WRAPPERS_ASSETGUARD_SYSCHECKD_SRC}
        ${WRAPPERS_ASSETGUARD_ASSETGUARD_DB_SRC}
        ${WRAPPERS_ASSETGUARD_ASSETGUARD_MODULES_SRC}
        ${WRAPPERS_ASSETGUARD_MONITORD_SRC}
        ${WRAPPERS_ASSETGUARD_OS_AUTH_SRC}
        ${WRAPPERS_ASSETGUARD_ADDAGENT_SRC}
        ${WRAPPERS_ASSETGUARD_CONFIG_SRC}
        ${WRAPPERS_CLIENT_AGENT_SRC}
        ${WRAPPERS_ASSETGUARD_REMOTED_SRC}
        ${WRAPPERS_DATA_PROVIDER_SRC}
        ${WRAPPERS_LOGCOLLECTOR_SRC}
        ${WRAPPERS_SHARED_MODULES_SRC}
        ${WRAPPERS_MACOS_SRC}
        ${WRAPPERS_MACOS_LIBC_SRC}
        ${WRAPPERS_MACOS_POSIX_SRC})

  else()
    # Linux uses POSIX wrappers with --wrap linker flag
    file(GLOB WRAPPERS_EXTERNALS_AUDIT_SRC
         "${SRC_FOLDER}/unit_tests/wrappers/externals/audit/*.c")
    file(GLOB WRAPPERS_EXTERNALS_PROCPC_SRC
         "${SRC_FOLDER}/unit_tests/wrappers/externals/procpc/*.c")
    file(GLOB WRAPPERS_LINUX_SRC "${SRC_FOLDER}/unit_tests/wrappers/linux/*.c")

    set(UNIT_TEST_WRAPPERS_SRC
        ${WRAPPERS_COMMON_SRC}
        ${WRAPPERS_EXTERNALS_SRC}
        ${WRAPPERS_EXTERNALS_BZIP2_SRC}
        ${WRAPPERS_EXTERNALS_ZLIB_SRC}
        ${WRAPPERS_EXTERNALS_CJSON_SRC}
        ${WRAPPERS_EXTERNALS_OPENSSL_SRC}
        ${WRAPPERS_EXTERNALS_SQLITE_SRC}
        ${WRAPPERS_EXTERNALS_PCRE2_SRC}
        ${WRAPPERS_LIBC_SRC}
        ${WRAPPERS_POSIX_SRC}
        ${WRAPPERS_ASSETGUARD_SRC}
        ${WRAPPERS_ASSETGUARD_OS_CRYPTO_SRC}
        ${WRAPPERS_ASSETGUARD_OS_EXECD_SRC}
        ${WRAPPERS_ASSETGUARD_OS_NET_SRC}
        ${WRAPPERS_ASSETGUARD_OS_REGEX_SRC}
        ${WRAPPERS_ASSETGUARD_OS_XML_SRC}
        ${WRAPPERS_ASSETGUARD_SHARED_SRC}
        ${WRAPPERS_ASSETGUARD_SYSCHECKD_SRC}
        ${WRAPPERS_ASSETGUARD_ASSETGUARD_DB_SRC}
        ${WRAPPERS_ASSETGUARD_ASSETGUARD_MODULES_SRC}
        ${WRAPPERS_ASSETGUARD_MONITORD_SRC}
        ${WRAPPERS_ASSETGUARD_OS_AUTH_SRC}
        ${WRAPPERS_ASSETGUARD_ADDAGENT_SRC}
        ${WRAPPERS_ASSETGUARD_CONFIG_SRC}
        ${WRAPPERS_CLIENT_AGENT_SRC}
        ${WRAPPERS_ASSETGUARD_REMOTED_SRC}
        ${WRAPPERS_DATA_PROVIDER_SRC}
        ${WRAPPERS_LOGCOLLECTOR_SRC}
        ${WRAPPERS_SHARED_MODULES_SRC}
        ${WRAPPERS_EXTERNALS_AUDIT_SRC}
        ${WRAPPERS_EXTERNALS_PROCPC_SRC}
        ${WRAPPERS_LINUX_SRC})
  endif()

endif()

# Create the production assetguard library (without test wrappers)
add_library(assetguard STATIC ${LIBASSETGUARD_SRC})

# Create a separate test library with wrappers for unit tests only
if(UNIT_TEST)
  add_library(assetguard_test STATIC ${LIBASSETGUARD_SRC} ${UNIT_TEST_WRAPPERS_SRC})
endif()

# Set properties: library name, output directory
set_target_properties(
  assetguard
  PROPERTIES OUTPUT_NAME "assetguard"
             LINKER_LANGUAGE C
             ARCHIVE_OUTPUT_DIRECTORY ${SRC_FOLDER}/build/lib
             LIBRARY_OUTPUT_DIRECTORY ${SRC_FOLDER}/build/lib
             POSITION_INDEPENDENT_CODE ON)

# Add compile definitions
target_compile_definitions(assetguard PRIVATE ARGV0="assetguard")

if(OS_BIG_ENDIAN)
  add_definitions(-DOS_BIG_ENDIAN)
endif(OS_BIG_ENDIAN)

if(CA_NAME)
  target_compile_definitions(assetguard PRIVATE CA_NAME="${CA_NAME}")
endif()

if(IMAGE_TRUST_CHECKS)
  target_compile_definitions(assetguard
                             PRIVATE IMAGE_TRUST_CHECKS=${IMAGE_TRUST_CHECKS})
endif()

if(ENABLE_AUDIT)
  target_compile_definitions(assetguard PRIVATE ENABLE_AUDIT)
endif()

target_link_libraries(assetguard PUBLIC assetguardext)

# Configure assetguard_test library for unit tests
if(UNIT_TEST)
  # Set properties for test library
  set_target_properties(
    assetguard_test
    PROPERTIES OUTPUT_NAME "assetguard_test"
               LINKER_LANGUAGE C
               ARCHIVE_OUTPUT_DIRECTORY ${SRC_FOLDER}/build/lib
               LIBRARY_OUTPUT_DIRECTORY ${SRC_FOLDER}/build/lib
               POSITION_INDEPENDENT_CODE ON)

  # Add same compile definitions as production library
  target_compile_definitions(assetguard_test PRIVATE ARGV0="assetguard")
  target_compile_definitions(assetguard_test PRIVATE ASSETGUARD_UNIT_TESTING)

  if(CA_NAME)
    target_compile_definitions(assetguard_test PRIVATE CA_NAME="${CA_NAME}")
  endif()

  if(IMAGE_TRUST_CHECKS)
    target_compile_definitions(assetguard_test
                               PRIVATE IMAGE_TRUST_CHECKS=${IMAGE_TRUST_CHECKS})
  endif()

  if(ENABLE_AUDIT)
    target_compile_definitions(assetguard_test PRIVATE ENABLE_AUDIT)
  endif()

  # Debug flags for unit tests: -g -O0
  target_compile_options(assetguard_test PUBLIC -g -O0)

  # Add coverage libraries and flags for unit tests
  add_coverage_libraries(assetguard_test)

  # Link with assetguardext
  target_link_libraries(assetguard_test PUBLIC assetguardext)
endif()

# Create shared library (Linux/server only — used by the engine)
if(NOT IS_AGENT AND CMAKE_SYSTEM_NAME STREQUAL "Linux")
  # Linux: libassetguardshared.so
  add_library(assetguardshared SHARED ${LIBASSETGUARD_SRC})

  set_target_properties(
    assetguardshared
    PROPERTIES OUTPUT_NAME "assetguardshared"
               LIBRARY_OUTPUT_DIRECTORY ${SRC_FOLDER}/build/lib
               BUILD_WITH_INSTALL_RPATH TRUE
               INSTALL_RPATH "$ORIGIN"
               POSITION_INDEPENDENT_CODE ON)

  target_compile_definitions(assetguardshared PRIVATE ARGV0="assetguard")
  # Link with assetguardext using -Wl,--whole-archive (Linux linker flag)
  target_link_libraries(assetguardshared PUBLIC -Wl,--whole-archive assetguardext
                                           -Wl,--no-whole-archive)

  # Apply common compile definitions to shared library
  if(CA_NAME)
    target_compile_definitions(assetguardshared PRIVATE CA_NAME="${CA_NAME}")
  endif()

  if(IMAGE_TRUST_CHECKS)
    target_compile_definitions(assetguardshared
                               PRIVATE IMAGE_TRUST_CHECKS=${IMAGE_TRUST_CHECKS})
  endif()

  if(ENABLE_AUDIT)
    target_compile_definitions(assetguardshared PRIVATE ENABLE_AUDIT)
  endif()
endif()
