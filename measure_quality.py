
from cipher.quality import calculate_mse, calculate_psnr

original = "samples/cover.png"
modified = "output/hidden.png"

mse = calculate_mse(original, modified)
psnr = calculate_psnr(original, modified)

print("\nCipherVeil Image Quality Report")
print("--------------------------------")
print(f"MSE:  {mse:.6f}")
print(f"PSNR: {psnr:.2f} dB" if mse else "PSNR: Infinite")
