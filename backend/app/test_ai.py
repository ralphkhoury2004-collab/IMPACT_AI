from ai_infer import predict_event

tests = [
    r"..\..\ai\data\events\event_0005",  # no crash
    r"..\..\ai\data\events\event_0070",  # light crash
    r"..\..\ai\data\events\event_0110",  # heavy crash
]

for p in tests:
    print("\nTesting event:", p)
    print(predict_event(p))
