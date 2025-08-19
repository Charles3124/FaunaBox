from PIL import Image, ImageDraw, ImageFilter


def white_to_green(input_path: str, output_path: str) -> None:
    # 打开图像，确保为 RGBA 模式（有透明度）
    img = Image.open(input_path).convert("RGBA")
    pixels = img.load()

    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            # 跳过完全透明像素
            if a == 0:
                continue

            # 判断是否接近白灰色调：R≈G≈B
            if abs(r - g) < 20 and abs(g - b) < 20:
                brightness = (r + g + b) // 3  # 亮度
                green = max(100, min(255, brightness))
                pixels[x, y] = (int(green * 0.3), green, int(green * 0.3), a)

    img.save(output_path)
    print(f"转换完成，保存为：{output_path}")


def white_to_green_with_outline(input_path: str, output_path: str, outline_color: tuple[int, int, int, int] = (0, 0, 0, 255),
                                outline_width: int = 5) -> None:
    # 打开图像，确保为 RGBA 模式（有透明度）
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()

    # 创建一张草体绿色化的新图像
    green_img = Image.new("RGBA", img.size)
    green_pixels = green_img.load()

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            if abs(r - g) < 20 and abs(g - b) < 20:
                brightness = (r + g + b) // 3
                green = max(100, min(255, brightness))
                green_pixels[x, y] = (int(green * 0.3), green, int(green * 0.3), a)
            else:
                green_pixels[x, y] = (r, g, b, a)  # 保留非白色像素

    # 创建轮廓图（黑白）
    mask = green_img.split()[3].point(lambda p: 255 if p > 0 else 0)
    outline_mask = mask.filter(ImageFilter.MaxFilter(outline_width * 2 + 1))  # 扩大透明边界
    outline_mask = Image.eval(outline_mask, lambda p: 255 if p > 0 else 0)

    # 创建最终图像：先填轮廓颜色，再贴上草图
    final_img = Image.new("RGBA", img.size)
    draw = ImageDraw.Draw(final_img)
    for y in range(height):
        for x in range(width):
            if outline_mask.getpixel((x, y)) == 255 and green_pixels[x, y][3] == 0:
                draw.point((x, y), fill=outline_color)

    # 将绿色草贴上去
    final_img = Image.alpha_composite(final_img, green_img)
    final_img.save(output_path)
    print(f"草图转换完成，已保存为：{output_path}")


white_to_green("D:/My Programs/Animals World Game/pics/PNG/Shaded/sprite_0055.png",
               "D:/My Programs/Animals World Game/pics/grass1.png")
