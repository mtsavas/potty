def merge_to_ass(en_file, tr_file, output_file):
    def parse_srt(file_path):
        with open(file_path, encoding='utf-8') as f:
            content = f.read().split('\n\n')
        blocks = []
        for block in content:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                blocks.append({
                    'index': lines[0],
                    'time': lines[1],
                    'text': '\n'.join(lines[2:])
                })
        return blocks

    def srt_time_to_ass(srt_time):
        return srt_time.replace(',', '.')

    en_blocks = parse_srt(en_file)
    tr_blocks = parse_srt(tr_file)

    with open(output_file, 'w', encoding='utf-8') as f:
        # ASS HEADER
        f.write("[Script Info]\n")
        f.write("Title: Dual Subtitle\n")
        f.write("ScriptType: v4.00+\n")
        f.write("PlayResX: 1280\n")
        f.write("PlayResY: 720\n")
        f.write("WrapStyle: 0\n")
        f.write("ScaledBorderAndShadow: yes\n\n")

        # STYLES
        f.write("[V4+ Styles]\n")
        f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
                "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
                "MarginR, MarginV, Encoding\n")
        # Türkçe stili (ÜSTTE - Ekranın alt kısmında): Beyaz yazı, siyah arka plan
        f.write("Style: TR,Arial,30,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1.5,0,2,10,10,50,1\n")
        # İngilizce stili (ALTTA - Ekranın daha alt kısmında): Sarı yazı, siyah arka plan
        f.write("Style: EN,Arial,30,&H0000FFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1.5,0,2,10,10,130,1\n\n")

        # EVENTS
        f.write("[Events]\n")
        f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")

        # Satırları eşleştirip birleştiriyoruz
        for en, tr in zip(en_blocks, tr_blocks):
            start_time = srt_time_to_ass(en['time'].split(' --> ')[0])
            end_time = srt_time_to_ass(en['time'].split(' --> ')[1])

            en_text = en['text'].replace('\n', ' ')
            tr_text = tr['text'].replace('\n', ' ')

            # Türkçe (ÜST - Ekranın alt kısmında) ve İngilizce (ALT - Daha aşağıda)
            f.write(f"Dialogue: 0,{start_time},{end_time},TR,,0,0,0,,{tr_text}\n")
            f.write(f"Dialogue: 1,{start_time},{end_time},EN,,0,0,0,,{en_text}\n")

# Dosya isimlerini belirt ve fonksiyonu çağır:
merge_to_ass("english.srt", "turkish.srt", "dual_subs.ass")