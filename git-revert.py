import subprocess
import sys
from os.path import dirname
from mojo import UI

BACKUP_SUFFIX = '.bak'

def toggle_glyph_from_head(font, glyph):
    """Toggle between git HEAD version of glyph and current modified version
 
    Keyword arguments:
    font -- font object
    glyph -- glyph object   
    """
    
    try:
        restore_modified_glyph(font, glyph)
    except KeyError:
        if git_glyph_changed(font.path, glyph.name):
            swap_glyph_from_head(font,glyph)
        else:
            print("Glyph is same as in HEAD")

def swap_glyph_from_head(font, glyph):
    """Replace a glyph with the version of it from git HEAD
    
    Keyword arguments:
    font -- font object
    glyph -- glyph object
    """

    # get glyph version from head
    glyph_head = git_glyph(CurrentFont(), CurrentGlyph().name, "HEAD")

    # backup current modified glyph version
    backupGlyph = font.insertGlyph(CurrentGlyph(), name = glyph.name + BACKUP_SUFFIX)
    
    # replace current glyph with version from git
    font[glyph.name] = glyph_head
    
    
def restore_modified_glyph(font, glyph):
    """Replace a glyph with the copied "backup" version within the font
    
    Keyword arguments:
    font -- font object
    glyph -- glyph object
    """
    
    # restore 
    font[glyph.name] = font[glyph.name + BACKUP_SUFFIX]
    font.removeGlyph(glyph.name + BACKUP_SUFFIX)

    
def git_path(path):
    """Get the path git uses to refer to a file
    
    Keyword arguments:
    path -- the absolute path to a file
    """
    
    cwd = dirname(path)
    completed = subprocess.run(['git', 'ls-files', '--full-name', path], stdout=subprocess.PIPE, cwd=cwd, check=True)
    return completed.stdout.decode('utf-8').strip()
    
def git_root_path(path):
    """Get the root directory of the git repository
    
    Keyword arguments:
    path -- the absolute path to a file
    """
    
    completed = subprocess.run(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE, cwd=dirname(path), check=True)
    return completed.stdout.decode('utf-8').strip()

def git_file(path, revision):
    """Get a version of a file (blob) from its git repository
    
    Keyword arguments:
    path -- the absolute path to a file
    revison -- the git revision (such as "HEAD")
    """
    
    relative_path = git_path(path)
    cwd = git_root_path(path)
    completed = subprocess.run(['git', 'show', ("%s:%s") % (revision, relative_path)], stdout=subprocess.PIPE, cwd=cwd, check=True)
    return completed.stdout.decode('utf-8')
    
def git_glyph(font, glyph_name, revision):
    """Get a version of a glif from its git repository
    
    Keyword arguments:
    glyph_name -- name of the glyph
    revison -- the git revision (such as "HEAD")
    """
    
    # read the .glif file into a string
    path = glyph_path(font.path, glyph_name)
    glif_string = git_file(path, revision)
    
    # return a new glyph from the file string
    glyph = RGlyph()
    glyph.readGlyphFromString(glif_string)
    
    return glyph
    
def glyph_path(font_path, glyph_name):
    """Get the absolute path of a glif
    
    Keyword arguments:
    font_path -- path of a UFO directory
    revison -- the git revision (such as "HEAD")
    """
    
    return "%s/glyphs/%s.glif" % (font_path, glyph_name)
    
    
def git_glyph_changed(font_path, glyph_name):
    """check if a glyph has been modified from git HEAD
    
    Keyword arguments:
    font_path -- path of a UFO directory
    glyph_name -- name of the glyph
    """
    
    return git_file_changed(glyph_path(font_path, glyph_name))
    
    
def git_file_changed(path):
    """check if a file has been modified from git HEAD
    
    Keyword arguments:
    path -- the absolute path to a file
    """
    
    relative_path = git_path(path)
    cwd = git_root_path(path)
    completed = subprocess.run(['git', 'diff', '--exit-code', relative_path], stdout=subprocess.PIPE, cwd=cwd)
    
    # git diff --exit-code returns 0 when file not modified, and 1 when modified
    # simply convert into boolean
    return bool(completed.returncode)

    

font = CurrentFont()

try:
    glyph = CurrentGlyph()
    toggle_glyph_from_head(font, glyph)
    UI.CurrentSpaceCenter().refreshGlyphLineView()
except:
    print("No glyph selected!")






