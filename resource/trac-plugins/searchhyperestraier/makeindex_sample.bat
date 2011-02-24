
set EXPORT_FOLDER=E:\RepositorySearch\rep
set REPOS_URI=file:///e:/SVNrepo/MyRepository/trunk/test3
set INDEX_FOLDER=E:\RepositorySearch\casket

rmdir /S /Q %EXPORT_FOLDER%
svn export %REPOS_URI% %EXPORT_FOLDER%
rmdir /S /Q %INDEX_FOLDER%
estcmd gather -cl -fx .pdf,.rtf,.doc,.xls,.ppt T@estxfilt -ic CP932  -pc CP932  -sd %INDEX_FOLDER% %EXPORT_FOLDER%