# -*- coding: utf-8 -*-
import re
def is_valid_cbu(cbu):
  
  def cbu_v2(v1):
    mod = v1 % 10
    return 0 if mod == 0 else (10 - mod)

  def cbu_v1(pos1, pos2):
    M = [9, 7, 1, 3]  
    total = 0; i = pos2; j = -1
    while i >= pos1:
      if (j == -1): j = 3
      total += int(cbu[i]) * M[j]
      i -= 1; j -= 1

    return cbu_v2(total);
  
  if re.match(r"[0-9]{22}$", cbu) is None:
    return False

  if int(cbu[7]) != cbu_v1(0, 6):
    return False

  if int(cbu[21]) != cbu_v1(8, 20):
    return False

  return True


print is_valid_cbu('0150804601000112908741')