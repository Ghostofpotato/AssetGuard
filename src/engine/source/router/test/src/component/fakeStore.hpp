#ifndef _COMPONENT_FAKE_STORE_HPP
#define _COMPONENT_FAKE_STORE_HPP

constexpr auto ROUTER_JSON {R"([])"};

constexpr auto TESTER_JSON {R"([])"};

constexpr auto POLICY_JSON {
    R"({"name":"policy/assetguard/0","hash":"12403460954181119054","assets":["integration/assetguard-core-fake/0"]})"};

constexpr auto EPS_JSON {
    R"({
    "eps": 1,
    "refreshInterval": 1,
    "active": false
})"};

constexpr auto INTEGRATION_JSON {R"({
"name": "integration/assetguard-core-fake/0",
"decoders": ["decoder/fake/0"]}
)"};

auto constexpr DECODER_JSON = R"e({
    "name": "decoder/fake/0",
    "normalize": [
        {
        "map": [
            {
            "assetguard.message": "I am an fake decoder"
            }
        ]
        }
    ]
    })e";

auto constexpr ASSETGUARD_LOGPAR_TYPES_JSON = R"({
    "fields": {
        "assetguard.message": "text"
    }
}
)";

#endif // _COMPONENT_FAKE_STORE_HPP
