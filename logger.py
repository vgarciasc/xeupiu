def save_everything(img_ss, img_tb, img_tb_bw, lines):
    img_ss.save("data/tmp_window.png")
    img_tb.save("data/tmp_text.png")
    img_tb_bw.save("data/tmp_text_bw.png")
    for i, line in enumerate(lines):
        line.save(f"data/tmp_line_{i}.png")