import re
with open(r"D:\neon_unified\neon_architect.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the MODELS dictionary to use nemotron-3-ultra as primary with high thinking
old_models = """MODELS: Dict[str, Dict[str, Any]] = {
    "glm-5.2": {
        "id": "z-ai/glm-5.2",
        "name": "GLM-5.2",
        "provider": "NVIDIA NIM",
        "rpm": 40,
        # Was 8192. GLM-5.2 defaults to Think-Max reasoning and can produce
        # long chains of thought before the tool-call/content tokens even
        # start; Together's own quickstart warns to "set max_tokens
        # generously" when thinking is on, or the reasoning can eat the
        # whole budget and truncate the actual tool call mid-JSON.
        "max_tokens": 32768,
        "ctx_window": 131072,
        "thinking": False,
        "extra_body": None,
        "temperature": None,
        "top_p": None,
    },
    "glm-5.2-fp8": {
        "id": "z-ai/glm-5.2-fp8",
        "name": "GLM-5.2-FP8",
        "provider": "NVIDIA NIM",
        "rpm": 40,
        "max_tokens": 32768,
        "ctx_window": 131072,
        "thinking": False,
        "extra_body": None,
        "temperature": None,
        "top_p": None,
    },
    "minimax-m3": {
        "id": "minimaxai/minimax-m3",
        "name": "MiniMax M3",
        "provider": "NVIDIA NIM",
        "rpm": 40,
        # MoE, 1M context, native tool-calling/agent support per NVIDIA's
        # own deployment docs -- used here as a fast, large-context fallback
        # behind GLM-5.2/GLM-5.2-FP8.
        "max_tokens": 16384,
        "ctx_window": 1000000,
        "thinking": False,
        "extra_body": None,
        "temperature": 1.0,
        "top_p": 0.95,
    },
    "laguna-xs-2.1": {
        "id": "poolside/laguna-xs-2.1",
        "name": "Laguna XS 2.1",
        "provider": "NVIDIA NIM",
        "rpm": 40,
        # Poolside's 33B-total/3B-active MoE, purpose-built for agentic
        # coding/tool-use/long-horizon work, 262K context, native
        # interleaved reasoning + tool calls.
        "max_tokens": 16384,
        "ctx_window": 262144,
        "thinking": True,
        "extra_body": None,
        "temperature": 0.3,
        "top_p": 0.95,
    },
    "kimi-k2-thinking": {
        "id": "moonshotai/kimi-k2-thinking",
        "name": "Kimi K2 Thinking",
        "provider": "NVIDIA NIM",
        "rpm": 40,
        # Moonshot's 1T-total/32B-active MoE, confirmed on NVIDIA NIM's
        # catalog (LLM APIs section, docs.api.nvidia.com/nim/reference/
        # moonshotai-kimi-k2-thinking). Native INT4, 256K context, and
        # its own tool-call parsing pipeline explicitly documented to
        # stay coherent across 200-300 consecutive tool calls without
        # drift -- the single most agentic-tool-use-focused model in this
        # fallback chain. NVIDIA's model card recommends temperature=1.0.
        # Always runs in thinking mode (no non-thinking variant).
        "max_tokens": 16384,
        "ctx_window": 262144,
        "thinking": True,
        "extra_body": None,
        "temperature": 1.0,
        "top_p": None,
    },
}"""

new_models = """MODELS: Dict[str, Dict[str, Any]] = {
    "nemotron-3-ultra": {
        "id": "nvidia/nemotron-3-ultra-550b-a55b",
        "name": "Nemotron 3 Ultra",
        "provider": "NVIDIA NIM",
        "rpm": 40,
        # NVIDIA's 53B parameter ultra model with strong reasoning and tool-use.
        # High thinking mode for complex multi-step tasks.
        "max_tokens": 32768,
        "ctx_window": 131072,
        "thinking": True,
        "extra_body": {"reasoning": {"effort": "high"}},
        "temperature": 0.3,
        "top_p": 0.95,
    },
    "glm-5.2": {
        "id": "z-ai/glm-5.2",
        "name": "GLM-5.2",
        "provider": "NVIDIA NIM",
        "rpm": 40,
        # Was 8192. GLM-5.2 defaults to Think-Max reasoning and can produce
        # long chains of thought before the tool-call/content tokens even
        # start; Together's own quickstart warns to "set max_tokens
        # generously" when thinking is on, or the reasoning can eat the
        # whole budget and truncate the actual tool call mid-JSON.
        "max_tokens": 32768,
        "ctx_window": 131072,
        "thinking": False,
        "extra_body": None,
        "temperature": None,
        "top_p": None,
    },
    "glm-5.2-fp8": {
        "id": "z-ai/glm-5.2-fp8",
        "name": "GLM-5.2-FP8",
        "provider": "NVIDIA NIM",
        "rpm": 40,
        "max_tokens": 32768,
        "ctx_window": 131072,
        "thinking": False,
        "extra_body": None,
        "temperature": None,
        "top_p": None,
    },
    "minimax-m3": {
        "id": "minimaxai/minimax-m3",
        "name": "MiniMax M3",
        "provider": "NVIDIA NIM",
        "rpm": 40,
        # MoE, 1M context, native tool-calling/agent support per NVIDIA's
        # own deployment docs -- used here as a fast, large-context fallback
        # behind GLM-5.2/GLM-5.2-FP8.
        "max_tokens": 16384,
        "ctx_window": 1000000,
        "thinking": False,
        "extra_body": None,
        "temperature": 1.0,
        "top_p": 0.95,
    },
    "laguna-xs-2.1": {
        "id": "poolside/laguna-xs-2.1",
        "name": "Laguna XS 2.1",
        "provider": "NVIDIA NIM",
        "rpm": 40,
        # Poolside's 33B-total/3B-active MoE, purpose-built for agentic
        # coding/tool-use/long-horizon work, 262K context, native
        # interleaved reasoning + tool calls.
        "max_tokens": 16384,
        "ctx_window": 262144,
        "thinking": True,
        "extra_body": None,
        "temperature": 0.3,
        "top_p": 0.95,
    },
    "kimi-k2-thinking": {
        "id": "moonshotai/kimi-k2-thinking",
        "name": "Kimi K2 Thinking",
        "provider": "NVIDIA NIM",
        "rpm": 40,
        # Moonshot's 1T-total/32B-active MoE, confirmed on NVIDIA NIM's
        # catalog (LLM APIs section, docs.api.nvidia.com/nim/reference/
        # moonshotai-kimi-k2-thinking). Native INT4, 256K context, and
        # its own tool-call parsing pipeline explicitly documented to
        # stay coherent across 200-300 consecutive tool calls without
        # drift -- the single most agentic-tool-use-focused model in this
        # fallback chain. NVIDIA's model card recommends temperature=1.0.
        # Always runs in thinking mode (no non-thinking variant).
        "max_tokens": 16384,
        "ctx_window": 262144,
        "thinking": True,
        "extra_body": None,
        "temperature": 1.0,
        "top_p": None,
    },
}"""

content = content.replace(old_models, new_models)

# Also update DEFAULT_CONFIG to use nemotron-3-ultra as default
content = content.replace('"default_model": "glm-5.2"', '"default_model": "nemotron-3-ultra"')

# Update phase_models to use nemotron for testing/verification
content = content.replace(
    '''"phase_models": {
        "testing": "minimax-m3",
        "verification": "minimax-m3",
    },''',
    '''"phase_models": {
        "testing": "nemotron-3-ultra",
        "verification": "nemotron-3-ultra",
    },'''
)

with open(r"D:\neon_unified\neon_architect.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
