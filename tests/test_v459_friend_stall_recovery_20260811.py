import ast, types, unittest
from pathlib import Path
import cv2
ROOT=Path(__file__).resolve().parents[1]
HOOK=ROOT/'portable'/'hook.py'
FIX=ROOT/'tests'/'fixtures'/'live-v459-friend-help-stalled-sanitized-20260811.png'
def load_functions(*names):
 s=HOOK.read_text(encoding='utf-8-sig'); t=ast.parse(s); wanted=set(names); nodes=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in wanted]; m=ast.Module(body=nodes,type_ignores=[]); ast.fix_missing_locations(m); ns={}; exec(compile(m,str(HOOK),'exec'),ns); return ns
class V459FriendStallTests(unittest.TestCase):
 def test_visible_friend_action_recovery_owns_stalled_page(self):
  ns=load_functions('_qqfarm_visible_friend_action_recovery')
  self.assertIn('_qqfarm_visible_friend_action_recovery',ns)
  frame=cv2.imread(str(FIX)); calls=[]; ctx=types.SimpleNamespace()
  ns.update({'_friend_guard_friend_ui_state':lambda f: True,'_friend_selected_carousel_card_bounds':lambda f:{'left':123},'_friend_guard_help_button_match':lambda f:{'matched':True},'_friend_guard_steal_button_match':lambda f:{'matched':False},'_invoke_friend_actions_before_home':lambda c,f:(calls.append(f) or True,'help'),'_write':lambda *a:None})
  self.assertEqual((True,'help'),ns['_qqfarm_visible_friend_action_recovery'](ctx,frame))
  self.assertEqual(1,len(calls))
if __name__=='__main__': unittest.main()
