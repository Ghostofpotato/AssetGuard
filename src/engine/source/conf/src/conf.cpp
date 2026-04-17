#include <conf/conf.hpp>

#include <filesystem>
#include <unistd.h>

#include <base/process.hpp>
#include <fmt/format.h>

#include <conf/keys.hpp>

namespace conf
{

using namespace internal;

Conf::Conf(std::shared_ptr<IFileLoader> fileLoader)
    : m_fileLoader(fileLoader)
    , m_loaded(false)
{
    if (!m_fileLoader)
    {
        throw std::invalid_argument("The file loader cannot be null.");
    }

    // fs path
    const std::filesystem::path assetguardRoot = base::process::getAssetGuardHome();

    // Register available configuration units with Default Settings

    // Logging module
    addUnit<int>(key::LOGGING_LEVEL, "ASSETGUARD_LOG_LEVEL", 0);

    // Standalone Logging module
    addUnit<std::string>(key::STANDALONE_LOGGING_LEVEL, "ASSETGUARD_STANDALONE_LOG_LEVEL", "info");

    // Store module
    addUnit<std::string>(key::STORE_PATH, "ASSETGUARD_STORE_PATH", (assetguardRoot / "engine/store").c_str());

    // Default outputs
    addUnit<std::string>(key::OUTPUTS_PATH, "ASSETGUARD_OUTPUTS_PATH", (assetguardRoot / "engine/outputs/").c_str());

    // Default kvdb ioc
    addUnit<std::string>(key::KVDB_IOC_PATH, "ASSETGUARD_KVDB_IOC_PATH", (assetguardRoot / "engine/kvdb-ioc").c_str());

    // Content Manager
    addUnit<std::string>(key::CM_RULESET_PATH, "ASSETGUARD_CM_RULESET_PATH", (assetguardRoot / "etc/ruleset").c_str());
    addUnit<size_t>(key::CM_SYNC_INTERVAL, "ASSETGUARD_CM_SYNC_INTERVAL", 120);
    addUnit<size_t>(key::IOC_SYNC_INTERVAL, "ASSETGUARD_IOC_SYNC_INTERVAL", 360);

    // Geo module
    addUnit<size_t>(key::GEO_SYNC_INTERVAL, "ASSETGUARD_GEO_SYNC_INTERVAL", 360);
    addUnit<std::string>(key::GEO_DB_PATH, "ASSETGUARD_GEO_DB_PATH", (assetguardRoot / "engine/mmdb").c_str());
    addUnit<std::string>(key::GEO_MANIFEST_URL,
                         "ASSETGUARD_GEO_MANIFEST_URL",
                         "https://assetguard-cloud-cti-web-components-dev.s3.us-east-2.amazonaws.com/maxmind_geoip/manifest.json");

    // Indexer connector
    addUnit<std::vector<std::string>>(key::INDEXER_HOST, "ASSETGUARD_INDEXER_HOSTS", {"http://localhost:9200"});
    addUnit<std::string>(key::INDEXER_USER, "ASSETGUARD_INDEXER_USER", "admin");
    addUnit<std::string>(key::INDEXER_PASSWORD, "ASSETGUARD_INDEXER_PASSWORD", "admin");
    addUnit<std::vector<std::string>>(key::INDEXER_SSL_CA_BUNDLE, "ASSETGUARD_INDEXER_SSL_CA_BUNDLE", {});
    addUnit<std::string>(key::INDEXER_SSL_CERTIFICATE, "ASSETGUARD_INDEXER_SSL_CERTIFICATE", "");
    addUnit<std::string>(key::INDEXER_SSL_KEY, "ASSETGUARD_INDEXER_SSL_KEY", "");

    // Raw Event Indexer
    addUnit<bool>(key::RAW_EVENT_INDEXER_ENABLED, "ASSETGUARD_RAW_EVENT_INDEXER_ENABLED", false);

    // RemoteConfig Indexer
    addUnit<size_t>(key::REMOTE_CONF_SYNC_INTERVAL, "ASSETGUARD_REMOTE_CONF_SYNC_INTERVAL", 300);

    // Queue event module
    addUnit<size_t>(key::EVENT_QUEUE_SIZE, "ASSETGUARD_EVENT_QUEUE_SIZE", 0x1 << 17);
    addUnit<size_t>(key::EVENT_QUEUE_EPS, "ASSETGUARD_EVENT_QUEUE_EPS", 0);

    // Orchestrator module
    addUnit<int>(key::ORCHESTRATOR_THREADS, "ASSETGUARD_ORCHESTRATOR_THREADS", 0);

    // Http server module
    addUnit<std::string>(
        key::SERVER_API_SOCKET, "ASSETGUARD_SERVER_API_SOCKET", (assetguardRoot / "queue/sockets/analysis").c_str());
    addUnit<int>(key::SERVER_API_TIMEOUT, "ASSETGUARD_SERVER_API_TIMEOUT", 5000);
    addUnit<int64_t>(key::SERVER_API_PAYLOAD_MAX_BYTES, "ASSETGUARD_SERVER_API_PAYLOAD_MAX_BYTES", 0);

    // Event server - enriched (http)
    addUnit<std::string>(key::SERVER_ENRICHED_EVENTS_SOCKET,
                         "ASSETGUARD_SERVER_ENRICHED_EVENTS_SOCKET",
                         (assetguardRoot / "queue/sockets/queue-http.sock").c_str());

    // Enable or disable server event processing
    addUnit<bool>(key::SERVER_ENABLE_EVENT_PROCESSING, "ASSETGUARD_SERVER_ENABLE_EVENT_PROCESSING", true);

    // TZDB module
    addUnit<std::string>(key::TZDB_PATH, "ASSETGUARD_TZDB_PATH", (assetguardRoot / "queue/tzdb").c_str());
    addUnit<bool>(key::TZDB_AUTO_UPDATE, "ASSETGUARD_TZDB_AUTO_UPDATE", false);
    addUnit<std::string>(key::TZDB_FORCE_VERSION_UPDATE, "ASSETGUARD_TZDB_FORCE_VERSION_UPDATE", "");

    // Streamlog module
    addUnit<std::string>(key::STREAMLOG_BASE_PATH, "ASSETGUARD_STREAMLOG_BASE_PATH", (assetguardRoot / "logs/").c_str());
    addUnit<bool>(key::STREAMLOG_SHOULD_COMPRESS, "ASSETGUARD_STREAMLOG_SHOULD_COMPRESS", true);
    addUnit<size_t>(key::STREAMLOG_COMPRESSION_LEVEL, "ASSETGUARD_STREAMLOG_COMPRESSION_LEVEL", 5);
    addUnit<std::string>(
        key::STREAMLOG_ALERTS_PATTERN, "ASSETGUARD_STREAMLOG_ALERTS_PATTERN", "${YYYY}/${MMM}/assetguard-${name}-${DD}.json");
    addUnit<size_t>(key::STREAMLOG_ALERTS_MAX_SIZE, "ASSETGUARD_STREAMLOG_ALERTS_MAX_SIZE", 0);
    addUnit<size_t>(key::STREAMLOG_ALERTS_BUFFER_SIZE, "ASSETGUARD_STREAMLOG_ALERTS_BUFFER_SIZE", 0x1 << 20);
    addUnit<std::string>(
        key::STREAMLOG_ARCHIVES_PATTERN, "ASSETGUARD_STREAMLOG_ARCHIVES_PATTERN", "${YYYY}/${MMM}/assetguard-${name}-${DD}.json");
    addUnit<size_t>(key::STREAMLOG_ARCHIVES_MAX_SIZE, "ASSETGUARD_STREAMLOG_ARCHIVES_MAX_SIZE", 0);
    addUnit<size_t>(key::STREAMLOG_ARCHIVES_BUFFER_SIZE, "ASSETGUARD_STREAMLOG_ARCHIVES_BUFFER_SIZE", 0x1 << 20);

    // Archiver module
    addUnit<bool>(key::ARCHIVER_ENABLED, "ASSETGUARD_ARCHIVER_ENABLED", false);

    // Process module
    addUnit<std::string>(key::PID_FILE_PATH, "ASSETGUARD_ENGINE_PID_FILE_PATH", (assetguardRoot / "var/run/").c_str());
    addUnit<std::string>(key::GROUP, "ASSETGUARD_ENGINE_GROUP", "assetguard-manager");
    addUnit<bool>(key::SKIP_GROUP_CHANGE, "ASSETGUARD_SKIP_GROUP_CHANGE", false);

    // API modules
    addUnit<int64_t>(key::API_RESOURCE_PAYLOAD_MAX_BYTES, "ASSETGUARD_SERVER_API_MAX_RESOURCE_PAYLOAD_SIZE", 50'000);
    addUnit<int64_t>(
        key::API_RESOURCE_KVDB_PAYLOAD_MAX_BYTES, "ASSETGUARD_SERVER_API_MAX_RESOURCE_KVDB_PAYLOAD_SIZE", 100'000);
};

void Conf::validate(const OptionMap& config) const
{
    for (const auto& [key, unit] : m_units)
    {
        auto it = config.find(key);
        if (it == config.end())
        {
            continue; // The configuration is not set for this key, ignore it
        }

        const auto& valueStr = it->second;
        const auto unitType = unit->getType();
        switch (unitType)
        {
            case UnitConfType::INTEGER:
            {
                std::size_t pos = 0;
                try
                {
                    auto v = std::stoll(valueStr, &pos);

                    if (pos != valueStr.size())
                    {
                        throw std::runtime_error(fmt::format(
                            "Invalid configuration type for key '{}'. Extra characters found in integer: '{}'.",
                            key,
                            valueStr.substr(pos)));
                    }
                }
                catch (const std::invalid_argument& e)
                {
                    throw std::runtime_error(
                        fmt::format("Invalid configuration type for key '{}'. Could not parse '{}'.", key, valueStr));
                }
                catch (const std::out_of_range& e)
                {
                    throw std::runtime_error(
                        fmt::format("Invalid configuration type for key '{}'. Value out of range for integer: '{}'.",
                                    key,
                                    valueStr));
                }

                break;
            }

            case UnitConfType::STRING:
            {
                break;
            }

            case UnitConfType::STRING_LIST:
            {
                // Detect list-style formatting with brackets: [a,b]
                if (valueStr.front() == '[' && valueStr.back() == ']')
                {
                    throw std::runtime_error(fmt::format(
                        "Invalid configuration type for key '{}'. Bracket notation '[...]' is not allowed: '{}'.",
                        key,
                        valueStr));
                }

                break;
            }

            case UnitConfType::BOOL:
            {
                std::string lowerVal = valueStr;
                std::transform(lowerVal.begin(), lowerVal.end(), lowerVal.begin(), ::tolower);
                if (lowerVal != "true" && lowerVal != "false")
                {
                    throw std::runtime_error(fmt::format(
                        "Invalid configuration type for key '{}'. Expected boolean, got '{}'.", key, valueStr));
                }
                break;
            }

            default: throw std::logic_error(fmt::format("Invalid configuration type for key '{}'.", key));
        }
    }
}

void Conf::load()
{
    if (m_loaded)
    {
        throw std::logic_error("The configuration is already loaded.");
    }
    m_loaded = true;

    // Only load the internal configuration if we are not in standalone mode
    if (!base::process::isStandaloneModeEnable())
    {
        auto fileConf = (*m_fileLoader)();
        validate(fileConf);
        m_fileConfig = std::move(fileConf);
    }
}

} // namespace conf
