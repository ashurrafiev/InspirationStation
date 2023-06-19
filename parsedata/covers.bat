for /r %%f in (*.webm) do ffmpeg -y -i "%%~nf.webm" -vf "select=eq(n\,0)" -q:v 4 "%%~nf.jpg"
