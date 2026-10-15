
| Cosa vi serve | Pygame | Equivalente MLX | Esito / limiti |
| ------------- | ------ | ---------------- | -------------- |
| Window + loop | `pygame.display.set_mode`, `pygame.event.pump` | `mlx_new_window`, `mlx_loop` | Functional equivalent |
| Disegno labirinto/sprite come immagini | `blit()` di superfici/immagini | `mlx_put_image_to_window` | Equivalente funzionale |
| Input tastiera | `pygame.event.get()` + `KEYDOWN` | `mlx_key_hook` | Functional equivalent: per gli eventi usati |
| Testo HUD (score, vite) | `pygame.font.Font + render()` | `mlx_string_put` | Solo font bitmap semplice; niente TTF con stili/dimensioni variabili |
| Forme geometriche con fill | `pygame.draw.circle/rect/polygon` | No equivalent MLX primitives | Non usare; usare immagini pre-renderizzate |
| Audio | `pygame.mixer` | No Functional equivalent | To be avoided or justified as a non-core extra. |
| Lettura buffer pixel | `pygame.image.tobytes(surface, format)` | `mlx_get_data_addr(img, &bpp, &line_length, &endian)` | Functional equivalent: Both allow for reading the pixels; the MLX layout requires interpretation. |
| Creazione immagine da buffer | `pygame.image.frombytes(bytes, size, format)` | `mlx_new_image` + `mlx_get_data_addr` + copy the bytes into the buffer | Functional equivalent: ccopy while maintaining dimensions and format |
| Scaling immagini nearest-neighbor | `nearest_neighbor_scale` con NumPy | Lettura/scrittura dei pixel tramite `mlx_get_data_addr` | Algorithm reproducible in MLX with nearest-neighbor sampling |
| Scaling con filtro | `pygame.transform.smoothscale` / `rotozoom` | no Functional equivalent | Non usare nel progetto |
| Dimensioni desktop | `pygame.display.Info()` | `mlx_get_screen_size(mlx_ptr, &sizex, &sizey)` | Partial: The code uses only width/height; the other fields of `Info` are not permitted. |
| Presentazione del frame | `pygame.display.flip()` | `mlx_put_image_to_window(...)` + `mlx_do_sync(mlx_ptr)` | Functional equivalent; MLX does not have an explicit flip. |
| Auto-repeat tastiera | Not configured; `pygame.key.set_repeat` not used | `mlx_do_key_autorepeatoff/on(mlx_ptr)` | No delays or intervals are set; navigation uses discrete presses. |
| Timer | `pygame.time.Clock` | Gestione del tempo nel loop hook | concettual equivalent |

`nearest_neighbor` resizes images by directly sampling RGBA pixels at integer coordinates. This operation occurs upon loading or resizing—rather than during every frame—and can be replicated by reading from and writing to the buffer via `mlx_get_data_addr`. The MLX target uses 32 bpp (4 bytes per pixel), whereas `pygame.image.tobytes` allows for explicitly requesting `RGBA`. Consequently, the MLX port requires reordering bytes according to the reported endianness and addressing rows using `line_length`, without assuming the MLX buffer shares the same RGBA byte order produced by Pygame.

In the code, `pygame.display.Info()` reads only `current_w` and `current_h`, both at startup and when returning from fullscreen mode. Timed key repetition is not configured; navigation responds to each individual key press without enforcing custom intervals.
