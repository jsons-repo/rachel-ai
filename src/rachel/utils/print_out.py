# src/rachel/utils/print_out.py

from rachel.core.config import get_config
from rachel.utils.common import debug

audio_cfg = get_config().audio
summarization_cfg = get_config().summarization

def print_audio_config(audio_cfg, FORMAT):
    # Print configuration
    print("*" * 60)
    print("Audio Configuration")
    print(f"\tchunk_duration             = {audio_cfg.chunk_duration}s")
    print(f"\toverlap_duration           = {audio_cfg.overlap_duration}s")
    print(f"\tchunk                      = {audio_cfg.chunk} samples")
    print(f"\tchannels                   = {audio_cfg.channels}")
    print(f"\trate                       = {audio_cfg.rate} Hz")
    print(f"\tformat                     = {FORMAT} (paInt16)")
    print(f"\tsilence_threshold          = {audio_cfg.silence_threshold} (RMS)")

def print_audio_capture_started():
    print("\n" * 5)
    print("- " * 30)
    print("Audio capture started...")
    print("- " * 30)
    print("\n" * 5)

def print_audio_device_list(pa):
    for idx in range(pa.get_device_count()):
        dev = pa.get_device_info_by_index(idx)
        print(f"Device {idx}: {dev['name']}")

def print_shallow_config(shallow_cfg):
    print("*" * 60)
    print("Shallow LLM Configuration")
    print(f"\trepo                       = {shallow_cfg.repo}")
    print(f"\tname                       = {shallow_cfg.name}")
    print(f"\tbackend                    = {shallow_cfg.backend}")
    print(f"\tdevice                     = {shallow_cfg.device}")
    print(f"\tcompute_type               = {shallow_cfg.compute_type}")
    print(f"\tdo_sample                  = {shallow_cfg.do_sample}")
    print(f"\ttemperature                = {shallow_cfg.temperature}")
    print(f"\tmax_tokens                 = {shallow_cfg.max_tokens}")
    print(f"\trepetition_penalty         = {shallow_cfg.repetition_penalty}")
    print(f"\ttop_k                      = {shallow_cfg.top_k}")
    print(f"\ttop_p                      = {shallow_cfg.top_p}")
    print(f"\tctx_window_tokens          = {shallow_cfg.ctx_window_tokens}")
    print(f"\ttrust_remote_code          = {shallow_cfg.trust_remote_code}")
    print(f"\tshallow_context_window     = {summarization_cfg.shallow_context_window}")

def print_shallow_prompt(prompt:str):
    debug("Shallow Prompt:", prompt)

def print_shallow_outputs(raw_llm_output, parsed_flag_output, semantic_summary):
    print("\n" * 2)
    print("✅ Shallow LLM Response")
    print(f"\tOutput: {raw_llm_output}")
    print(f"\tParsed Flags: {parsed_flag_output}")
    print(f"\tSemantic Summary: {semantic_summary}")
    print("\n" * 2)

def print_flags_detected(parsed_flag_output):
    print("\n" * 2)
    print("✅ Flags detected ")
    print("parsed_flag_output:", parsed_flag_output)
    print("\n" * 2)

def print_no_flags():
    print("\n" * 2)
    print("✅ No Flags Found")
    print("Pushing to shallow_queue_results...")
    print("\n" * 2)

def print_deep_client_result(result_text, duration):
    print("\n" * 2)
    print("✅ Deep LLM Response")
    print("\tDuration:", duration)
    print(f"\tOutput:{result_text}")
    print("\n" * 2)

def print_deep_client_inputs(shallow_context, generated_prompt):
    print("\n" * 2)
    print("Generated deep input text:", shallow_context.text)
    print("Generated deep prompt:", generated_prompt)
    print("\n" * 2)