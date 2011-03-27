UPDATE enum SET name = '対応済' WHERE type ='resolution' AND value = '1';
UPDATE enum SET name = '不正' WHERE type ='resolution' AND value = '2';
UPDATE enum SET name = '対応しない' WHERE type ='resolution' AND value = '3';
UPDATE enum SET name = '重複' WHERE type ='resolution' AND value = '4';
UPDATE enum SET name = '再現しない' WHERE type ='resolution' AND value = '5';
UPDATE enum SET name = '最重要' WHERE type ='priority' AND value = '1';
UPDATE enum SET name = '重要' WHERE type ='priority' AND value = '2';
UPDATE enum SET name = '普通' WHERE type ='priority' AND value = '3';
UPDATE enum SET name = '低い' WHERE type ='priority' AND value = '4';
UPDATE enum SET name = '最低' WHERE type ='priority' AND value = '5';
UPDATE component SET name='チームA' WHERE name = 'component1';
UPDATE component SET name='チームB' WHERE name = 'component2';
UPDATE milestone SET name ='スプリント0(準備)', description='[/burndown?selected_milestone=スプリント0(準備) バーンダウンチャートへのリンク][[BR]]開発の準備のスプリント。開発環境の準備、全体のアーキテクチャデザイン、プロトタイプ検証などを実施' WHERE name = 'milestone1';
UPDATE milestone SET name ='スプリント1', description='[/burndown?selected_milestone=スプリント1 バーンダウンチャートへのリンク][[BR]]スプリント1' WHERE name = 'milestone2';
UPDATE milestone SET name ='スプリント3', description='[/burndown?selected_milestone=スプリント2 バーンダウンチャートへのリンク][[BR]]スプリント2' WHERE name = 'milestone3';
UPDATE milestone SET name ='スプリント4(リリース準備)', description='[/burndown?selected_milestone=スプリント4(リリース準備) バーンダウンチャートへのリンク][[BR]]リリース準備のためのスプリント' WHERE name = 'milestone4';
DELETE FROM version WHERE name = '1.0';
DELETE FROM version WHERE name = '2.0';
UPDATE enum SET name = 'ストーリー' WHERE type ='ticket_type' AND value = '1';
UPDATE enum SET name = 'タスク' WHERE type ='ticket_type' AND value = '2';
UPDATE enum SET name = 'バグ' WHERE type ='ticket_type' AND value = '3';
INSERT INTO enum VALUES('ticket_type', '課題', '4');

INSERT INTO session_attribute values ('admin', '1','name','管理太郎');
INSERT INTO session_attribute values ('admin', '1','enabled','1');
INSERT INTO session_attribute values ('guest', '1','name','客人開発者');
INSERT INTO session_attribute values ('guest', '1','enabled','1');
INSERT INTO session_attribute values ('leader', '1','name','頭春蔵');
INSERT INTO session_attribute values ('leader', '1','enabled','1');
INSERT INTO attachment values ('wiki', 'UserManagerPluginPictures', 'admin-penguin.png',0,0,'admin', 'Avatar','127.0.0.1');
INSERT INTO attachment values ('wiki', 'UserManagerPluginPictures', 'guest-hamster.png',0,0,'guest', 'Avatar','127.0.0.1');
INSERT INTO attachment values ('wiki', 'UserManagerPluginPictures', 'leader-cat.png',0,0,'leader', 'Avatar','127.0.0.1');


INSERT INTO report VALUES(18,'trac',"バックログの確認",
"SELECT 
  CASE tt.status WHEN 'closed' THEN 5 WHEN 'new' THEN 3 ELSE 1 END AS __color__,
   (CASE tt.status 
      WHEN 'closed' THEN 'color: #777; background: #ddd; border-color: #ccc;'
      ELSE 
        (CASE tt.owner WHEN $USER THEN 'font-weight: bold' END)
    END) AS __style__,
  tt.milestone AS __group__,
  t.id AS id,
  '' AS 'ストーリー',
  tt.id AS ticket,
  tt.summary AS 'タスク',
  tt.owner AS '担当者', 
  tt.status AS '状態', 
  CASE WHEN st.child IS NULL THEN peh.value ELSE eh.value END AS '見積',
  CASE WHEN st.child IS NULL THEN pth.value ELSE th.value END AS '作業時間',
  '' AS description
FROM ticket t 
  LEFT JOIN subtickets st  ON st.parent =t.id AND t.type='ストーリー'
  LEFT JOIN ticket tt ON tt.id=st.child
  LEFT JOIN milestone m ON t.milestone = m.name 
  LEFT JOIN ticket_custom eh ON eh.ticket = tt.id AND eh.name = 'estimatedhours'
  LEFT JOIN ticket_custom th ON th.ticket = tt.id AND th.name = 'totalhours'
  LEFT JOIN ticket_custom peh ON peh.ticket = t.id AND peh.name = 'estimatedhours'
  LEFT JOIN ticket_custom pth ON pth.ticket = t.id AND pth.name = 'totalhours'
WHERE t.type='ストーリー'  AND st.child IS NOT NULL AND t.status <> 'closed'

UNION

SELECT
  4 AS __color__,
  'color: black; font-weight: bold;'  AS __style__,
  t.milestone AS __group__,
  t.id AS id,
  t.summary AS 'ストーリー',
  '',
  '',
  '',
  '',
  '',
  '',
  '[/newticket?type=タスク&parents='||t.id||'&milestone='||t.milestone||' タスク作成]' AS  description
FROM ticket t
WHERE t.type='ストーリー' AND t.status<>'closed'

UNION

SELECT
  CASE t.status WHEN 'closed' THEN 5 WHEN 'new' THEN 3 ELSE 1 END AS __color__,
   (CASE t.status 
      WHEN 'closed' THEN 'color: #777; background: #ddd; border-color: #ccc;'
      ELSE 
        (CASE t.owner WHEN $USER THEN 'font-weight: bold' END)
    END) AS __style__,
  t.milestone AS __group__,
  '-' AS id,
  'その他:' ||t.type AS 'ストーリー',
  t.id AS ticket,
  t.summary as 'タスク',
  t.owner AS '担当者', 
  t.status AS '状態',
  eh.value AS '見積',
  th.value AS '作業時間',
  ''
FROM ticket as t
  LEFT JOIN ticket_custom eh ON eh.ticket = t.id AND eh.name = 'estimatedhours'
  LEFT JOIN ticket_custom th ON th.ticket = t.id AND th.name = 'totalhours'
WHERE NOT t.type IN ('ストーリー')  AND
  NOT EXISTS (SELECT * from subtickets WHERE subtickets.child = t.id)


ORDER BY __group__ DESC, id,ticket DESC","
 * スプリント毎のストーリー(プロダクトバックログ)とタスク(スプリントバックログ)を確認することができます。
 * 各スプリントのスプリントバックログ(タスク)の一覧を表示します。スプリントバックログはプロダクトバックログ(ストーリー)に紐づいている必要があります。
 * 一番右のタスク作成をクリックすると、ストーリーに対応したタスクを作成することができます。
 * クローズされたチケットはグレーで表示されます。
");


INSERT INTO report VALUES(19,'trac',"バックログの確認(チーム別)",
"SELECT 
  CASE tt.status WHEN 'closed' THEN 5 WHEN 'new' THEN 3 ELSE 1 END AS __color__,
   (CASE tt.status 
      WHEN 'closed' THEN 'color: #777; background: #ddd; border-color: #ccc;'
      ELSE 
        (CASE tt.owner WHEN $USER THEN 'font-weight: bold' END)
    END) AS __style__,
  tt.milestone AS __group__,
  t.id AS id,
  '' AS 'ストーリー',
  tt.id AS ticket,
  tt.summary AS 'タスク',
  tt.owner AS '担当者', 
  tt.status AS '状態', 
  CASE WHEN st.child IS NULL THEN peh.value ELSE eh.value END AS '見積',
  CASE WHEN st.child IS NULL THEN pth.value ELSE th.value END AS '作業時間',
  '' AS description
FROM ticket t 
  LEFT JOIN subtickets st  ON st.parent =t.id AND t.type='ストーリー'
  LEFT JOIN ticket tt ON tt.id=st.child
  LEFT JOIN milestone m ON t.milestone = m.name 
  LEFT JOIN ticket_custom eh ON eh.ticket = tt.id AND eh.name = 'estimatedhours'
  LEFT JOIN ticket_custom th ON th.ticket = tt.id AND th.name = 'totalhours'
  LEFT JOIN ticket_custom peh ON peh.ticket = t.id AND peh.name = 'estimatedhours'
  LEFT JOIN ticket_custom pth ON pth.ticket = t.id AND pth.name = 'totalhours'
WHERE t.component=$TEAM AND t.type='ストーリー'  AND st.child IS NOT NULL AND t.status <> 'closed' 

UNION

SELECT
  4 AS __color__,
  'color: black; font-weight: bold;'  AS __style__,
  t.milestone AS __group__,
  t.id AS id,
  t.summary AS 'ストーリー',
  '',
  '',
  '',
  '',
  '',
  '',
  '[/newticket?type=タスク&parents='||t.id||'&milestone='||t.milestone||' タスク作成]' AS  description
FROM ticket t
WHERE t.component=$TEAM AND t.type='ストーリー' AND t.status<>'closed'

UNION

SELECT
  CASE t.status WHEN 'closed' THEN 5 WHEN 'new' THEN 3 ELSE 1 END AS __color__,
   (CASE t.status 
      WHEN 'closed' THEN 'color: #777; background: #ddd; border-color: #ccc;'
      ELSE 
        (CASE t.owner WHEN $USER THEN 'font-weight: bold' END)
    END) AS __style__,
  t.milestone AS __group__,
  '-' AS id,
  'その他:' ||t.type AS 'ストーリー',
  t.id AS ticket,
  t.summary as 'タスク',
  t.owner AS '担当者', 
  t.status AS '状態',
  eh.value AS '見積',
  th.value AS '作業時間',
  ''
FROM ticket as t
  LEFT JOIN ticket_custom eh ON eh.ticket = t.id AND eh.name = 'estimatedhours'
  LEFT JOIN ticket_custom th ON th.ticket = t.id AND th.name = 'totalhours'
WHERE t.component=$TEAM AND NOT t.type IN ('ストーリー')  AND
  NOT EXISTS (SELECT * from subtickets WHERE subtickets.child = t.id)

ORDER BY __group__ DESC, id,ticket DESC","
 * チーム別のスプリントのストーリー(プロダクトバックログ)とタスク(スプリントバックログ)を確認することができます。
 * {{{[report:19?TEAM=チームA チームAのバックログ]}}}のように、レポートのリンク、もしくはURLの最後にTEAM変数でチーム名を指定して利用します。
 * 各スプリントのスプリントバックログ(タスク)の一覧を表示します。スプリントバックログはプロダクトバックログ(ストーリー)に紐づいている必要があります。
 * 一番右のタスク作成をクリックすると、ストーリーに対応したタスクを作成することができます。
 * クローズされたチケットはグレーで表示されます。
");



INSERT INTO report VALUES(20,'trac',"スプリント計画・担当者割り当て","
query:?status=accepted
&
status=assigned
&
status=new
&
status=reopened
&
type=タスク
&
group=milestone
&
col=id
&
col=parents
&
col=summary
&
col=type
&
col=priority
&
col=owner
&
col=estimatedhours
&
col=billable
&
col=status
&
order=priority,parents
","
このレポートはスプリント計画、担当者割り当てなどに利用します。

バッチ編集機能により、'''チェックしたチケットを一括して'''スプリントに割り当てたり、担当者を割り当てることができます。

 * プロダクトバックログは「集計に含める」をFalseに設定してください。
 * スプリントバックログは「集計に含める」をTrueにしてバーンダウンチャートの工数に含めるようにします。
 * スプリントバックログに対して見積時間を入力してください。
");

INSERT INTO report VALUES(21,'trac',"スプリント計画・プロダクトバックログの整理","
query:?status=accepted
&
status=assigned
&
status=new
&
status=reopened
&
type=ストーリーﾞ
&
group=milestone
&
col=id
&
col=summary
&
col=status
&
col=type
&
col=owner
&
col=priority
&
col=estimatedhours
&
col=billable
&
order=priority
","
このレポートはスプリント計画時にスプリントで実行するプロダクトバックログを選択するときに利用します。
 * 次のスプリントで実施するチケットにチェックを入れて、バッチ編集でマイルストーンを設定してください。
 * プロダクトバックログは「集計に含める」をFalseに設定してください。
");



