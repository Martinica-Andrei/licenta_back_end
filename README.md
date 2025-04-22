<div>
    <h3>Citations</h3> 
    <ul>
        <li>Mengting Wan, Julian McAuley, "<a href="https://mengtingwan.github.io/paper/recsys18_mwan.pdf">Item Recommendation on Monotonic Behavior Chains</a>", in RecSys'18. [<a href="https://dblp.uni-trier.de/rec/conf/recsys/WanM18.html?view=bibtex">bibtex</a>]
        </li>
        <li>Mengting Wan, Rishabh Misra, Ndapa Nakashole, Julian McAuley, "<a href="https://mengtingwan.github.io/paper/acl19_mwan.pdf">Fine-Grained Spoiler Detection from Large-Scale Review Corpora</a>", in ACL'19. [<a href="https://dblp.uni-trier.de/rec/conf/acl/WanMNM19.html?view=bibtex">bibtex</a>]
        </li>
    </ul>
</div>
<div>
    <h3>Downloading, analysis, and preprocessing of data were done on kaggle.</h3>
    <ul>
        <li><a href="https://www.kaggle.com/code/mrtinicandreimarian/goodreads-book-graph-datasets-download">Downloading</a></li>
        <li><a href="https://www.kaggle.com/code/mrtinicandreimarian/goodreads-book-graph-analysis">Analysis</a></li>
        <li><a href="https://www.kaggle.com/code/mrtinicandreimarian/goodreads-book-graph-data-preprocessing">Preprocessing</a></li>
    </ul>
</div>

Create virtual environment using python version 3.10.17.
pip install -r requirements.txt
modify alembic.ini connection string
modify app.secret_key (app.py) and store it somewhere outside the code

CHANGE OR SET IN /etc/mysql/my.cnf (mysql config file in linux)

[mysqld]
innodb_ft_min_token_size=1
log_bin_trust_function_creators = 1



Execute in shell: alembic upgrade head