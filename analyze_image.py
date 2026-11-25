
from cipher.steganalysis import analyze_lsb

image_path = input("Enter image path: ")

try:
    result = analyze_lsb(image_path)

    print("\nCipherVeil LSB Analysis Report")
    print("--------------------------------")

    print(f"Total LSBs: {result['total_bits']:,}")
    print(f"Zero bits: {result['zero_count']:,}")
    print(f"One bits: {result['one_count']:,}")

    print(f"Zero ratio: {result['zero_ratio']:.4f}")
    print(f"One ratio: {result['one_ratio']:.4f}")

    print(f"Chi-square: {result['chi_square']:.4f}")
    print(f"LSB entropy: {result['entropy']:.4f} bits")

    print("\nInterpretation:")

    if result["entropy"] > 0.95:
        print("LSB distribution is highly balanced.")
    else:
        print("LSB distribution is not highly balanced.")

    print(
        "Note: These statistics alone cannot establish "
        "whether an image contains hidden data."
    )

except (ValueError, OSError) as error:
    print(f"Analysis failed: {error}")
