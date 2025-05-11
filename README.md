# Program for searching for similar hieroglyphs 

The program shows the hieroglyphs that are most similar to the one you entered. There is a version with only hieroglyphs from hsk 3.0, there is an extended version with 20750 characters. There are Russian dictionary entries for all characters. English dictionary entries are based on https://github.com/ProxPxD/Hanzi_searcher/blob/master/cedict_ts.u8 as of 01.01.2025, and do not exist for all hieroglyphs.

1\. To use the program (HSK 3.0):

1.1 For \*nix user run setup.sh.

1.1.1 If any errors occure You need check that:

a) the files with the database archive have been merged:

*cat x\* \> zi.db.zip*

b) the archive with the database has been unpacked:

*unzip zi.db.zip*

c) pip has successfully installed all dependencies:

*pip install -r requirements.txt*

d) for the file start.sh the execution bit is set:

*chmod +x start.sh*

e) (optional) delete unnecessary files:

*rm -r x\**

rm zi.db.zip

1.2 Run start.sh.

1.3 For other os:

a) merge files with the database archive

b) unpack the database archive

c) install dependencies

d) launch the program:

*streamlit run zi_sim.py*

1.4 For working with hieroglyphs beyond HSK 3.0 (total 20750 characters):

a) Download the full version of the database from Google Drive:

https://drive.google.com/file/d/1USz8r-gm9wLhrBC5od2vHLvqNlxW-2hH/view?usp=drive_link

b) run the version that can work with the extended database:

*streamlit run zi_sim_full.py*

2\. To recreate your own database with embeddings:

a) install dependencies:

*pip install -r requirements\_full.tx*

b) read the comments in files 0_1\* to 3_3\*, make changes, and execute
the code in python
