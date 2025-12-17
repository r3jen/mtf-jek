# import streamlit as st
# import sqlite3
# import pandas as pd
# from datetime import datetime

# DB_NAME = "data.db"
# TABLE_USERS = "users"
# TABLE_AGREEMENTS = "agreements"
# TABLE_EVALS = "evaluations"


# # ===========================================
# #  DB CONNECTION
# # ===========================================
# def get_conn():
#     return sqlite3.connect(DB_NAME, check_same_thread=False)


# # ===========================================
# #  INIT DATABASE
# # ===========================================
# def init_db():
#     conn = get_conn()
#     c = conn.cursor()

#     # Tabel users
#     c.execute(f"""
#     CREATE TABLE IF NOT EXISTS {TABLE_USERS} (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         full_name TEXT,
#         username TEXT UNIQUE,
#         password TEXT,
#         created_at TEXT DEFAULT CURRENT_TIMESTAMP
#     );
#     """)

#     # Tabel agreements
#     c.execute(f"""
#     CREATE TABLE IF NOT EXISTS {TABLE_AGREEMENTS} (
#         agreementno TEXT,
#         name TEXT,
#         brand_category TEXT,
#         branchfullname TEXT,
#         ntf TEXT,
#         installmentamount TEXT,
#         address TEXT,
#         rt TEXT,
#         rw TEXT,
#         kelurahan TEXT,
#         kecamatan TEXT,
#         city TEXT,
#         zipcode TEXT,
#         agingdate TEXT,
#         daysoverdue TEXT,
#         installmentno TEXT,
#         installmentdate TEXT,
#         totalosprincipal TEXT,
#         contractstatus TEXT,
#         financetype TEXT,
#         customerid TEXT,
#         activityuser TEXT,
#         tgltarikdata TEXT
#     );
#     """)

#     # Tabel evaluations
#     c.execute(f"""
#     CREATE TABLE IF NOT EXISTS {TABLE_EVALS} (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         agreementno TEXT,
#         username TEXT,
#         q1 INTEGER, q2 INTEGER, q3 INTEGER, q4 INTEGER, q5 INTEGER,
#         q6 INTEGER, q7 INTEGER, q8 INTEGER, q9 INTEGER, q10 INTEGER,
#         q11 INTEGER, q12 INTEGER, q13 INTEGER, q14 INTEGER,
#         created_at TEXT DEFAULT CURRENT_TIMESTAMP
#     );
#     """)

#     conn.commit()
#     conn.close()


# # ===========================================
# #  AUTH FUNCTIONS
# # ===========================================
# def generate_username(fullname):
#     parts = fullname.split()
#     return f"{parts[0].lower()}.{parts[1].lower()}"


# def generate_password(fullname):
#     parts = fullname.split()
#     return f"{parts[0].capitalize()}{parts[1][0].upper()}"


# def validate_login(username, password):
#     conn = get_conn()
#     c = conn.cursor()
#     c.execute(f"SELECT full_name, password FROM {TABLE_USERS} WHERE username = ?", (username,))
#     row = c.fetchone()
#     conn.close()

#     if not row:
#         return False, None

#     full_name, correct_pw = row
#     if correct_pw == password:
#         return True, full_name
#     return False, None


# # ===========================================
# #  CHECK WHICH AGREEMENTS ARE ALREADY EVALUATED
# # ===========================================
# def get_evaluated_agreements(username):
#     conn = get_conn()
#     df = pd.read_sql_query(
#         f"SELECT DISTINCT agreementno FROM {TABLE_EVALS} WHERE username = ?",
#         conn,
#         params=[username]
#     )
#     conn.close()
#     return set(df["agreementno"].tolist())


# # ===========================================
# #  ADMIN DASHBOARD
# # ===========================================
# def admin_dashboard():
#     st.title("Admin Dashboard")

#     st.header("1. Upload User Activity (Generate Username & Password)")
#     uploaded_users = st.file_uploader("Upload file user list (CSV/XLSX) dengan kolom 'activityuser'", type=["csv", "xlsx"])

#     if uploaded_users:
#         df = pd.read_excel(uploaded_users) if uploaded_users.name.endswith("xlsx") else pd.read_csv(uploaded_users)

#         if "activityuser" not in df.columns:
#             st.error("Kolom 'activityuser' tidak ditemukan!")
#         else:
#             df["username"] = df["activityuser"].apply(generate_username)
#             df["password"] = df["activityuser"].apply(generate_password)

#             st.dataframe(df)

#             if st.button("Simpan ke Database"):
#                 conn = get_conn()
#                 df[["activityuser", "username", "password"]].to_sql(TABLE_USERS, conn, if_exists="append", index=False)
#                 conn.close()
#                 st.success("Berhasil menyimpan user!")

#     st.header("2. Upload Agreement Data")
#     uploaded_agreement = st.file_uploader("Upload data agreement", type=["csv", "xlsx"])

#     if uploaded_agreement:
#         df2 = pd.read_excel(uploaded_agreement) if uploaded_agreement.name.endswith("xlsx") else pd.read_csv(uploaded_agreement)
#         st.dataframe(df2.head())

#         if st.button("Simpan Agreement"):
#             conn = get_conn()
#             df2.to_sql(TABLE_AGREEMENTS, conn, if_exists="append", index=False)
#             conn.close()
#             st.success("Agreement data berhasil disimpan!")


# # ===========================================
# #  USER DASHBOARD
# # ===========================================
# def user_dashboard():
#     username = st.session_state["username"]
#     full_name = st.session_state["full_name"]

#     st.title("User Dashboard")
#     st.write(f"Selamat datang, **{full_name}**")
#     st.write("Berikut adalah data yang terkait dengan aktivitas Anda:")

#     # Load agreement data
#     conn = get_conn()
#     df = pd.read_sql_query(
#         f"SELECT rowid, * FROM {TABLE_AGREEMENTS} WHERE LOWER(activityuser) = LOWER(?)",
#         conn,
#         params=[full_name],
#     )
#     conn.close()

#     if df.empty:
#         st.warning("Tidak ada data agreement.")
#         return

#     evaluated = get_evaluated_agreements(username)

#     # === LIST VIEW ===
#     if "selected_agreement" not in st.session_state:
#         st.session_state["selected_agreement"] = None

#     if st.session_state["selected_agreement"] is None:
#         # Highlight evaluated agreements
#         def highlight(row):
#             if row["agreementno"] in evaluated:
#                 return ['background-color: #d4edda'] * len(row)
#             return [''] * len(row)

#         st.dataframe(df.style.apply(highlight, axis=1), use_container_width=True)

#         st.markdown("### Pilih data untuk evaluasi:")

#         selected = st.selectbox("Pilih Agreement No", df["agreementno"].tolist())

#         if st.button("Evaluate Record Ini"):
#             st.session_state["selected_agreement"] = selected
#             st.rerun()
#         return

#     # === DETAIL VIEW ===
#     agreementno = st.session_state["selected_agreement"]

#     st.markdown(f"## Evaluasi untuk Agreement No: **{agreementno}**")

#     if st.button("⬅️ Kembali ke daftar agreement"):
#         st.session_state["selected_agreement"] = None
#         st.rerun()

#     record = df[df["agreementno"] == agreementno].iloc[0]

#     detail_df = pd.DataFrame({
#         "Field": record.index,
#         "Value": record.values
#     })

#     st.markdown("### Detail Data")
#     st.dataframe(detail_df, use_container_width=True)

#     # === EVALUATION QUESTIONS ===
#     st.markdown("## Evaluasi Kualitas Data (14 Pertanyaan)")

#     QUESTIONS = [
#         "Apakah data nama customer terlihat konsisten?",
#         "Apakah nominal NTF sesuai format angka?",
#         "Apakah installment amount wajar untuk kategori brand?",
#         "Apakah alamat customer lengkap?",
#         "Apakah nilai days overdue tampak valid?",
#         "Apakah tanggal aging date masuk akal?",
#         "Apakah nomor installment urut secara logis?",
#         "Apakah total outstanding principal sesuai pola?",
#         "Apakah kategori brand_category tepat?",
#         "Apakah branchfullname sesuai wilayah?",
#         "Apakah kecamatan & kelurahan konsisten?",
#         "Apakah zipcode valid?",
#         "Apakah contractstatus masuk akal?",
#         "Apakah keseluruhan data terlihat wajar?",
#     ]

#     scores = []
#     for i, q in enumerate(QUESTIONS, start=1):
#         skor = st.selectbox(f"{i}. {q}", [1, 2, 3, 4, 5], key=f"q{i}")
#         scores.append(skor)

#     if st.button("Simpan Evaluasi"):
#         conn = get_conn()
#         conn.execute(
#             f"""
#             INSERT INTO {TABLE_EVALS} (
#                 agreementno, username,
#                 q1, q2, q3, q4, q5,
#                 q6, q7, q8, q9, q10,
#                 q11, q12, q13, q14
#             ) VALUES ({','.join(['?'] * 16)})
#             """,
#             [agreementno, username] + scores
#         )
#         conn.commit()
#         conn.close()

#         st.success("Evaluasi berhasil disimpan!")
#         st.session_state["selected_agreement"] = None
#         st.rerun()


# # ===========================================
# #  MAIN
# # ===========================================
# def main():
#     st.set_page_config(page_title="Activity User App", layout="wide")

#     # Fix left alignment
#     st.markdown("""
#     <style>
#     .main .block-container {
#         max-width: 2000px !important;
#         margin-left: 0 !important;
#         padding-left: 2rem !important;
#         padding-right: 2rem !important;
#     }
#     </style>
#     """, unsafe_allow_html=True)

#     init_db()

#     if "logged_in" not in st.session_state:
#         st.session_state["logged_in"] = False

#     if not st.session_state["logged_in"]:
#         st.title("Login Activity User")

#         username = st.text_input("Username")
#         password = st.text_input("Password", type="password")

#         if st.button("Login"):
#             ok, full_name = validate_login(username, password)
#             if ok:
#                 st.session_state["logged_in"] = True
#                 st.session_state["username"] = username
#                 st.session_state["full_name"] = full_name
#                 st.rerun()
#             else:
#                 st.error("Username atau password salah!")
#         return

#     # Logged in
#     st.sidebar.write(f"Login sebagai: **{st.session_state['full_name']}**")
#     if st.sidebar.button("Logout"):
#         st.session_state.clear()
#         st.rerun()

#     # Determine role
#     if st.session_state["username"] == "admin":
#         admin_dashboard()
#     else:
#         user_dashboard()


# if __name__ == "__main__":
#     main()



import streamlit as st
import sqlite3
import pandas as pd

DB_NAME = "data.db"

TABLE_USERS = "users"
TABLE_AGREEMENTS = "agreements"

TABLE_QUESTIONS = "pkpp_questions"
TABLE_EVALS = "evaluations"
TABLE_EVAL_ANSWERS = "evaluation_answers"

EXPECTED_AGREEMENT_COLUMNS = [
    "agreementno",
    "name",
    "brand_category",
    "branchfullname",
    "ntf",
    "installmentamount",
    "address",
    "rt",
    "rw",
    "kelurahan",
    "kecamatan",
    "city",
    "zipcode",
    "agingdate",
    "daysoverdue",
    "installmentno",
    "installmentdate",
    "totalosprincipal",
    "contractstatus",
    "financetype",
    "customerid",
    "activityuser",
    "tgltarikdata",
]

# Admin hardcoded
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# =========================
# DB
# =========================
def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # users
    c.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_USERS} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        username TEXT UNIQUE,
        password TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # agreements
    c.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_AGREEMENTS} (
        agreementno TEXT,
        name TEXT,
        brand_category TEXT,
        branchfullname TEXT,
        ntf TEXT,
        installmentamount TEXT,
        address TEXT,
        rt TEXT,
        rw TEXT,
        kelurahan TEXT,
        kecamatan TEXT,
        city TEXT,
        zipcode TEXT,
        agingdate TEXT,
        daysoverdue TEXT,
        installmentno TEXT,
        installmentdate TEXT,
        totalosprincipal TEXT,
        contractstatus TEXT,
        financetype TEXT,
        customerid TEXT,
        activityuser TEXT,
        tgltarikdata TEXT
    );
    """)

    # master questions (PKPP)
    c.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_QUESTIONS} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT,
        bobot REAL,
        faktor TEXT,
        satu TEXT,
        dua TEXT,
        tiga TEXT,
        empat TEXT,
        lima TEXT,
        desc1 TEXT,
        desc2 TEXT,
        desc3 TEXT,
        desc4 TEXT,
        desc5 TEXT
    );
    """)

    # evaluations header
    c.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_EVALS} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agreementno TEXT,
        username TEXT,
        total_bobot REAL,
        total_score_weighted REAL,
        final_score_pct REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # evaluation answers (long format)
    c.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_EVAL_ANSWERS} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evaluation_id INTEGER,
        agreementno TEXT,
        username TEXT,
        question_id INTEGER,
        description TEXT,
        faktor TEXT,
        bobot REAL,
        score INTEGER,
        score_label TEXT,
        score_desc TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()


# =========================
# AUTH (User generated from activityuser)
# =========================
def generate_username(fullname: str) -> str:
    parts = str(fullname).strip().split()
    if len(parts) >= 2:
        return f"{parts[0].lower()}.{parts[1].lower()}"
    return parts[0].lower()


def generate_password(fullname: str) -> str:
    parts = str(fullname).strip().split()
    if len(parts) >= 2:
        first = parts[0]
        return f"{first}{parts[1][0].upper()}"
    return parts[0]


def validate_user_login(username, password):
    conn = get_conn()
    row = conn.execute(
        f"SELECT full_name, password FROM {TABLE_USERS} WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()

    if not row:
        return False, None
    full_name, pw = row
    return (pw == password), full_name


# =========================
# Helpers
# =========================
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip().str.lower()
    return df


def check_agreement_columns(df: pd.DataFrame):
    missing = [c for c in EXPECTED_AGREEMENT_COLUMNS if c not in df.columns]
    extra = [c for c in df.columns if c not in EXPECTED_AGREEMENT_COLUMNS]
    return missing, extra


def get_evaluated_agreements(username: str):
    conn = get_conn()
    df = pd.read_sql_query(
        f"SELECT DISTINCT agreementno FROM {TABLE_EVALS} WHERE username = ?",
        conn,
        params=[username],
    )
    conn.close()
    return set(df["agreementno"].tolist())


def load_questions():
    conn = get_conn()
    df = pd.read_sql_query(
        f"""
        SELECT id, description, bobot, faktor, satu, dua, tiga, empat, lima, desc1, desc2, desc3, desc4, desc5
        FROM {TABLE_QUESTIONS}
        ORDER BY id ASC
        """,
        conn,
    )
    conn.close()
    return df


def save_evaluation_and_answers(agreementno, username, q_df, answers):
    """
    answers: list of dict:
      {question_id, score, score_label, score_desc, bobot, description, faktor}
    """
    total_bobot = float(q_df["bobot"].astype(float).sum())
    total_weighted = sum(a["score"] * float(a["bobot"]) for a in answers)
    final_pct = round((total_weighted / (total_bobot * 5.0)) * 100.0, 2) if total_bobot > 0 else 0.0

    conn = get_conn()
    c = conn.cursor()

    # insert header evaluation
    c.execute(
        f"""
        INSERT INTO {TABLE_EVALS} (agreementno, username, total_bobot, total_score_weighted, final_score_pct)
        VALUES (?, ?, ?, ?, ?)
        """,
        (agreementno, username, total_bobot, total_weighted, final_pct),
    )
    evaluation_id = c.lastrowid

    # insert answers
    rows = []
    for a in answers:
        rows.append(
            (
                evaluation_id,
                agreementno,
                username,
                int(a["question_id"]),
                a["description"],
                a["faktor"],
                float(a["bobot"]),
                int(a["score"]),
                a["score_label"],
                a["score_desc"],
            )
        )

    c.executemany(
        f"""
        INSERT INTO {TABLE_EVAL_ANSWERS} (
            evaluation_id, agreementno, username, question_id,
            description, faktor, bobot, score, score_label, score_desc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    conn.commit()
    conn.close()

    return total_bobot, total_weighted, final_pct


# =========================
# Admin Dashboard
# =========================
def admin_dashboard():
    st.title("Admin Dashboard")

    tab_users, tab_agreements, tab_questions = st.tabs(
        ["1) Upload User Activity", "2) Upload Agreement Data", "3) Upload Master Pertanyaan PKPP"]
    )

    with tab_users:
        st.subheader("Upload User Activity (kolom: activityuser)")
        f = st.file_uploader("Upload CSV/XLSX", type=["csv", "xlsx", "xls"], key="admin_users")

        if f is not None:
            df = pd.read_excel(f) if f.name.lower().endswith(("xlsx", "xls")) else pd.read_csv(f)
            df = normalize_columns(df)

            if "activityuser" not in df.columns:
                st.error("Kolom 'activityuser' tidak ditemukan.")
            else:
                df = df[["activityuser"]].dropna().drop_duplicates()
                df["full_name"] = df["activityuser"].astype(str).str.strip()
                df["username"] = df["full_name"].apply(generate_username)
                df["password"] = df["full_name"].apply(generate_password)

                preview = df[["full_name", "username", "password"]]
                st.dataframe(preview, use_container_width=True)

                if st.button("Simpan / Update Users"):
                    conn = get_conn()
                    c = conn.cursor()
                    for _, r in preview.iterrows():
                        c.execute(
                            f"""
                            INSERT INTO {TABLE_USERS} (full_name, username, password)
                            VALUES (?, ?, ?)
                            ON CONFLICT(username) DO UPDATE SET
                              full_name = excluded.full_name,
                              password = excluded.password
                            """,
                            (r["full_name"], r["username"], r["password"]),
                        )
                    conn.commit()
                    conn.close()
                    st.success("Users berhasil disimpan / diupdate.")

        # info total users
        conn = get_conn()
        total = conn.execute(f"SELECT COUNT(*) FROM {TABLE_USERS}").fetchone()[0]
        conn.close()
        st.info(f"Total users di database: {total}")

    with tab_agreements:
        st.subheader("Upload Agreement Data (harus sesuai field yang sudah kamu definisikan)")
        f = st.file_uploader("Upload CSV/XLSX", type=["csv", "xlsx", "xls"], key="admin_agreements")

        if f is not None:
            df = pd.read_excel(f) if f.name.lower().endswith(("xlsx", "xls")) else pd.read_csv(f)
            df = normalize_columns(df)

            st.dataframe(df.head(), use_container_width=True)

            missing, extra = check_agreement_columns(df)
            if missing:
                st.error(f"Kolom wajib hilang: {missing}")
            else:
                if extra:
                    st.warning(f"Ada kolom tambahan (diabaikan): {extra}")

                if st.button("Simpan Agreement ke DB"):
                    conn = get_conn()
                    df[EXPECTED_AGREEMENT_COLUMNS].to_sql(TABLE_AGREEMENTS, conn, if_exists="append", index=False)
                    conn.close()
                    st.success("Agreement data tersimpan.")

        conn = get_conn()
        total = conn.execute(f"SELECT COUNT(*) FROM {TABLE_AGREEMENTS}").fetchone()[0]
        conn.close()
        st.info(f"Total baris agreements: {total}")

    with tab_questions:
        st.subheader("Upload Master Pertanyaan PKPP")
        st.write("Kolom wajib: description, bobot, faktor, satu..lima, desc1..desc5")
        f = st.file_uploader("Upload CSV/XLSX", type=["csv", "xlsx", "xls"], key="admin_questions")

        if f is not None:
            q = pd.read_excel(f) if f.name.lower().endswith(("xlsx", "xls")) else pd.read_csv(f)
            q = normalize_columns(q)

            required = ["description", "bobot", "faktor", "satu", "dua", "tiga", "empat", "lima", "desc1", "desc2", "desc3", "desc4", "desc5"]
            missing = [c for c in required if c not in q.columns]
            if missing:
                st.error(f"Kolom master pertanyaan belum lengkap. Missing: {missing}")
            else:
                st.dataframe(q.head(20), use_container_width=True)

                if st.button("Simpan Master Pertanyaan (Replace)"):
                    conn = get_conn()
                    # replace: drop lalu insert ulang agar sinkron dengan file master
                    conn.execute(f"DELETE FROM {TABLE_QUESTIONS}")
                    conn.commit()

                    q[required].to_sql(TABLE_QUESTIONS, conn, if_exists="append", index=False)
                    conn.close()
                    st.success("Master pertanyaan PKPP tersimpan (replace).")

        # info total questions
        conn = get_conn()
        total = conn.execute(f"SELECT COUNT(*) FROM {TABLE_QUESTIONS}").fetchone()[0]
        conn.close()
        st.info(f"Total pertanyaan PKPP di database: {total}")


# =========================
# User Dashboard
# =========================
def user_dashboard():
    username = st.session_state["username"]
    full_name = st.session_state["full_name"]

    st.title("User Dashboard")
    st.write(f"Selamat datang, **{full_name}**")

    # Load agreements for this user (by activityuser)
    conn = get_conn()
    df = pd.read_sql_query(
        f"SELECT rowid, * FROM {TABLE_AGREEMENTS} WHERE LOWER(activityuser) = LOWER(?)",
        conn,
        params=[full_name],
    )
    conn.close()

    if df.empty:
        st.warning("Tidak ada data agreement untuk user ini.")
        return

    evaluated = get_evaluated_agreements(username)

    # session selected agreement
    if "selected_agreement" not in st.session_state:
        st.session_state["selected_agreement"] = None

    # LIST VIEW
    if st.session_state["selected_agreement"] is None:
        st.subheader("Daftar Agreement (milik kamu)")

        def highlight_done(row):
            return ["background-color: #d4edda"] * len(row) if row["agreementno"] in evaluated else [""] * len(row)

        st.dataframe(df.style.apply(highlight_done, axis=1), use_container_width=True)

        st.caption("Baris berwarna hijau = sudah pernah dievaluasi oleh kamu.")

        selected = st.selectbox("Pilih Agreement No untuk dievaluasi", df["agreementno"].tolist())
        if st.button("Evaluate"):
            st.session_state["selected_agreement"] = selected
            st.rerun()
        return

    # DETAIL VIEW
    agreementno = st.session_state["selected_agreement"]
    st.subheader(f"Evaluasi Agreement No: {agreementno}")

    col_back, col_status = st.columns([1, 2])
    with col_back:
        if st.button("⬅️ Back ke daftar"):
            st.session_state["selected_agreement"] = None
            st.rerun()
    with col_status:
        if agreementno in evaluated:
            st.success("Status: Sudah dievaluasi (warna hijau di list).")
        else:
            st.info("Status: Belum dievaluasi.")

    record = df[df["agreementno"] == agreementno].iloc[0]
    detail_df = pd.DataFrame({"Field": record.index, "Value": record.values})
    st.dataframe(detail_df, use_container_width=True)

    # Load PKPP questions
    q_df = load_questions()
    if q_df.empty:
        st.error("Master pertanyaan PKPP belum diupload oleh admin.")
        return

    st.divider()
    st.subheader("Form Penilaian PKPP")

    answers = []
    total_weighted_preview = 0.0
    total_bobot = float(q_df["bobot"].astype(float).sum())

    for _, q in q_df.iterrows():
        qid = int(q["id"])
        desc = str(q["description"])
        faktor = str(q["faktor"])
        bobot = float(q["bobot"])

        # ringkas (label satu..lima)
        label_map = {
            1: str(q["satu"]),
            2: str(q["dua"]),
            3: str(q["tiga"]),
            4: str(q["empat"]),
            5: str(q["lima"]),
        }
        # detail (desc1..desc5)
        desc_map = {
            1: str(q["desc1"]),
            2: str(q["desc2"]),
            3: str(q["desc3"]),
            4: str(q["desc4"]),
            5: str(q["desc5"]),
        }

        st.markdown(f"**{qid:02d}. {desc}**")
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1:
            st.caption(f"Faktor: {faktor}")
        with c2:
            st.caption(f"Bobot: {bobot}")
        with c3:
            score = st.selectbox(
                "Skor",
                [1, 2, 3, 4, 5],
                key=f"pkpp_score_{qid}",
                format_func=lambda x: f"{x} — {label_map[x]}",
            )

        with st.expander("Lihat pedoman skor 1–5"):
            for s in [1, 2, 3, 4, 5]:
                st.write(f"**{s} — {label_map[s]}**")
                st.caption(desc_map[s])

        weighted = bobot * score
        total_weighted_preview += weighted

        answers.append(
            {
                "question_id": qid,
                "description": desc,
                "faktor": faktor,
                "bobot": bobot,
                "score": score,
                "score_label": label_map[score],
                "score_desc": desc_map[score],
            }
        )

        st.caption(f"Skor tertimbang: {weighted:.2f}")
        st.divider()

    # Summary score
    final_pct_preview = round((total_weighted_preview / (total_bobot * 5.0)) * 100.0, 2) if total_bobot > 0 else 0.0
    s1, s2, s3 = st.columns(3)
    s1.metric("Total Bobot", f"{total_bobot:.2f}")
    s2.metric("Total Skor Tertimbang", f"{total_weighted_preview:.2f}")
    s3.metric("Final Score (%)", f"{final_pct_preview:.2f}")

    if st.button("💾 Simpan Evaluasi"):
        total_bobot_db, total_weighted_db, final_pct_db = save_evaluation_and_answers(
            agreementno=agreementno,
            username=username,
            q_df=q_df,
            answers=answers
        )
        st.success(f"Evaluasi tersimpan. Final Score: {final_pct_db:.2f}%")
        # balik ke list agar user lihat highlight hijau
        st.session_state["selected_agreement"] = None
        st.rerun()


# =========================
# MAIN
# =========================
def main():
    st.set_page_config(page_title="PKPP Evaluation App", layout="wide")
    init_db()

    # simple left-leaning container tweak (tetap minimal)
    st.markdown("""
    <style>
    .main .block-container {
        max-width: 1800px !important;
        margin-left: 0 !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        st.title("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            # Admin
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state["logged_in"] = True
                st.session_state["role"] = "admin"
                st.session_state["username"] = ADMIN_USERNAME
                st.session_state["full_name"] = "Administrator"
                st.rerun()

            # User
            ok, full_name = validate_user_login(username, password)
            if ok:
                st.session_state["logged_in"] = True
                st.session_state["role"] = "user"
                st.session_state["username"] = username
                st.session_state["full_name"] = full_name
                st.rerun()
            else:
                st.error("Username / password salah.")
        return

    # sidebar
    st.sidebar.write(f"Login: **{st.session_state['full_name']}**")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    # routing
    if st.session_state.get("role") == "admin":
        admin_dashboard()
    else:
        user_dashboard()


if __name__ == "__main__":
    main()
