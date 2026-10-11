# Helpers for driving Calori on the emulator. Source this file.
export MSYS_NO_PATHCONV=1
ADB=/h/android1/platform-tools/adb
QA=/h/flutter_apps/calori-qa
QAW=H:/flutter_apps/calori-qa
PKG=com.usmanghani.calori
# shot NAME -> evidence/NAME.png (full size) + work/view/NAME.jpg (40 %, for review)
shot() { mkdir -p $QA/work/view; $ADB exec-out screencap -p > "$QA/evidence/$1.png" && \
  python -I -c "from PIL import Image; im=Image.open(r'$QAW/evidence/$1.png').convert('RGB'); im.resize((432, int(im.height*432/im.width))).save(r'$QAW/work/view/$1.jpg', quality=82)"; }
tap() { $ADB shell input tap "$1" "$2"; sleep "${3:-0.8}"; }
type_() { $ADB shell input text "$1"; sleep 0.5; }
key() { $ADB shell input keyevent "$1"; sleep "${2:-0.8}"; }
back() { key 4 "${1:-1}"; }
swipe() { $ADB shell input swipe "$1" "$2" "$3" "$4" "${5:-300}"; sleep "${6:-0.8}"; }
launch() { $ADB shell monkey -p $PKG -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1; sleep "${1:-3}"; }
reset() { $ADB shell pm clear $PKG >/dev/null; launch "${1:-3}"; }
# ui: dump the accessibility tree as "text|desc|bounds" lines
ui() { $ADB shell uiautomator dump /sdcard/ui.xml >/dev/null 2>&1; $ADB shell cat /sdcard/ui.xml | python -I -c "
import sys,re
x=sys.stdin.read()
for m in re.finditer(r'<node [^>]*?text=\"([^\"]*)\"[^>]*?content-desc=\"([^\"]*)\"[^>]*?bounds=\"([^\"]*)\"', x):
    t,d,b=m.groups()
    if t or d: print(f'{t[:60]}|{d[:600]}|{b}')"; }
# tapl "Label" [n]: tap the centre of the n-th (default 1st) node whose text or desc contains Label
tapl() { local b; b=$(ui | grep -F -- "$1" | sed -n "${2:-1}p" | grep -oE '\[[0-9]+,[0-9]+\]\[[0-9]+,[0-9]+\]$'); \
  if [ -z "$b" ]; then echo "NOT FOUND: $1"; return 1; fi; \
  local x1 y1 x2 y2; read x1 y1 x2 y2 < <(echo "$b" | tr -c '0-9' ' '); tap $(( (x1+x2)/2 )) $(( (y1+y2)/2 )) "${3:-0.9}"; }
# txt: print just the visible labels, one per line
txt() { ui | cut -d'|' -f1,2 | tr '|' ' ' | sed 's/^ //'; }
# rec NAME SECONDS: background screen recording to videos/NAME.mp4 (pull with recpull NAME)
rec() { $ADB shell screenrecord --time-limit "${2:-60}" "/sdcard/$1.mp4" & }
recpull() { $ADB shell pkill -INT screenrecord 2>/dev/null; sleep 2; $ADB pull "/sdcard/$1.mp4" "$QAW/videos/$1.mp4" >/dev/null && $ADB shell rm "/sdcard/$1.mp4"; }
res() { python H:/flutter_apps/calori-qa/report/record.py "$@"; }
# btn "Label": print enabled=true/false for the first node whose desc contains Label
btn() { $ADB shell uiautomator dump /sdcard/ui.xml >/dev/null; $ADB shell cat /sdcard/ui.xml | grep -oE "<node[^>]*content-desc=\"[^\"]*$1[^\"]*\"[^>]*>" | head -1 | grep -oE 'enabled="[^"]*"'; }
to_body() { reset 3; tapl Male >/dev/null; type_ "${1:-30}"; tapl Continue >/dev/null; sleep 0.8; }
HFIELD="540 1015"; WFIELD="540 1517"
hw() { type_ "$1"; back 1; tap $WFIELD; type_ "$2"; back 1; }
# kb_off: press Back only if the soft keyboard is actually showing
kb_off() { if $ADB shell dumpsys input_method | grep -q "mInputShown=true"; then key 4 0.8; fi; }
hw() { type_ "$1"; kb_off; tap $WFIELD; type_ "$2"; kb_off; }
# setf X Y TEXT [ndel]: focus the field at X,Y, delete ndel chars and type TEXT in one fast burst
setf() { $ADB shell input tap "$1" "$2"; sleep 0.6; $ADB shell "input keyevent 123 $(printf '67 %.0s' $(seq 1 ${4:-6})); input text '$3'"; sleep 0.8; }
to_target() { reset 3; tapl "$1" >/dev/null; type_ "$2"; tapl Continue >/dev/null; sleep 0.8; hw "$3" "$4"; tapl Continue >/dev/null; sleep 1; }
verdict() { ui | grep -oE 'Target weight[^|]*' | sed 's/&#10;/ /g'; }
# pair A B OUT: put two view images side by side (cropped to top 60 %) for one review read
pair() { python -I -c "
from PIL import Image
a=Image.open(r'$QAW/work/view/$1.jpg'); b=Image.open(r'$QAW/work/view/$2.jpg'); h=int(a.height*${4:-0.6})
o=Image.new('RGB',(a.width*2+10,h),'white'); o.paste(a.crop((0,0,a.width,h)),(0,0)); o.paste(b.crop((0,0,b.width,h)),(a.width+10,0)); o.save(r'$QAW/work/view/$3.jpg',quality=80)"; }
PLUS="970 2041"; CAMERA="540 2256"; HOMETAB="238 2287"; GOALTAB="841 2287"; CALBTN="110 262"
FFDIR=/h/tools/ffmpeg/ffmpeg-9.0.1-essentials_build/bin
# sheet_num VALUE: on an open number sheet, replace the value and press Save
sheet_num() { sleep 0.8; $ADB shell "input keyevent 123 67 67 67 67 67 67; input text '$1'"; sleep 0.6; tapl "Save" 1 1.5; }
card() { ui | sed 's/&#10;/ · /g' | grep -E "DAILY TARGET|Set your daily|suggests|below the" | cut -d'|' -f2 | tr '\n' ' ' | cut -c1-400; }
onboard_ref() { to_target Male 30 178 78; setf 700 785 "${1:-72}"; kb_off; sleep 0.8; tapl Continue 1 1.2; tapl "Moderately active" 1 2; tapl "Start tracking" 1 3; }
IMG_cat="179 1411"; IMG_chapati="540 1411"; IMG_apple="901 1411"; IMG_dal="179 1772"; IMG_salad="540 1772"; IMG_egg="901 1772"; IMG_biryani="179 2133"
paid() { local n; n=$(( $(cat $QA/work/paid_calls.txt) + 1 )); echo $n > $QA/work/paid_calls.txt; echo "paid call #$n"; }
review() { ui | sed 's/&#10;/ · /g' | cut -d'|' -f2 | grep -vE "^(Back|Close)$" | head -30 | cut -c1-200; }
