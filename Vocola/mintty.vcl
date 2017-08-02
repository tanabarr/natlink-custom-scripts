# Voice commands for mintty

#include Unimacro.vch;
include keys.vch;
include vim.vch;
include vim_plugins.vch;
include screen.vch;
include UNIX_shell.vch;

package (manager=|install|remove|update|upgrade|search|search all=searchall) = "apt-cyg $1 ";

