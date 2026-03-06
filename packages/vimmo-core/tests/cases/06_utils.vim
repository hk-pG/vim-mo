" VimMo test utility — global functions for import test
function! VimmoAdd(a, b)
  return a:a + a:b
endfunction

function! VimmoGreet(name)
  return "Hello, " .. a:name
endfunction
