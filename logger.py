def save_everything(img_ss, img_tb, img_tb_bw, lines):
    img_ss.save("data/tmp/window.png")
    img_tb.save("data/tmp/text.png")
    img_tb_bw.save("data/tmp/text_bw.png")
    for i, line in enumerate(lines):
        line.save(f"data/tmp/line_{i}.png")