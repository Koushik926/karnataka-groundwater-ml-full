"""
student_personal_local.py - the five students' contact details.

NOT IN GIT. Listed in .gitignore, because the repository is public and four of
these people are not the repository owner: their e-mail addresses, LinkedIn
profiles and Google Drive resume links are theirs to publish, not mine.

student_personal.py imports CONTACT from here if the file exists. Without it
every contact field is empty, which prints a ruled line in the report and omits
the coding-platform line altogether - so the build still works on a fresh clone,
it just produces documents with the personal fields left to be filled in by hand.
"""

CONTACT: dict[str, dict[str, str]] = {
    'NITIN G A': dict(
        email='nitinga2005@gmail.com',
        linkedin='https://www.linkedin.com/in/nitin-g-a-dev',
        github='https://github.com/Nitin-G-A',
        resume='https://drive.google.com/file/d/1Niu-zcqK6-EcXezHBFGymUQk6xCNjD-y/view',
    ),
    'R KOUSHIK': dict(
        email='rottelakoushik@gmail.com',
        linkedin='https://www.linkedin.com/in/koushik-r9',
        github='https://github.com/Koushik926',
        resume='https://drive.google.com/file/d/189AqZ89xWUmOqzXPlHjaooA7bARsl_yy/view',
        platform='HackerRank — hackerrank.com/profile/rottelakoushik',
    ),
    'S VARSHITH SAI': dict(
        email='varshith123a@gmail.com',
        linkedin='https://www.linkedin.com/in/varshith-sai-a59a85344',
        github='https://github.com/varshith-sai67',
        resume='https://drive.google.com/file/d/1dTCMV5m2kUdBBjs9YcUWixfniQkmNi2U/view',
    ),
    'BHIMISETTY KARTHIK': dict(
        email='bhimisettykarthik357@gmail.com',
        linkedin='https://www.linkedin.com/in/karthik-bhimisetty-010024298',
        github='https://github.com/karthikbhimisetty',
        resume='https://drive.google.com/file/d/1BXtt0Lqw-gUk2CfJM7pSfp5OBGCcmN2b/view',
        platform='LeetCode — leetcode.com/u/karthikbhimisetty',
    ),
    'G M CHANDRASHEKAR': dict(
        email='gmchandru50@gmail.com',
        linkedin='https://www.linkedin.com/in/chandrashekhar-gm-070228345',
        github='https://github.com/gmchandru50-ui',
        resume='https://drive.google.com/file/d/19LFYIC1wNwnaUixow2B5UMOpxlq08n0-/view',
    ),
}
