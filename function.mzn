function var int: find_last(array[int] of var int: x, var int: el)=
    max( [ if x[i] == el then i else 0 endif | i in index_set(x)]);

function var int: find_first(array[int] of var int: x, var int: el)=
   let{var int: return= min( [ if x[i] == el then i else max(index_set(x))+1 endif | i in index_set(x)])} in
   if return == max(index_set(x)) + 1
   then 0
   else return
   endif;
    
