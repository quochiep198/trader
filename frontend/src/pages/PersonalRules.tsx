import React, { useEffect, useState } from 'react';
import styles from '../styles/css/PersonalRules.module.css';
import api from '../services/api';
import { MessageProperties } from '../services/message';

interface Rule {
  id: string;
  user_id: string;
  rule_type: string;
  rule_value: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const RULE_METADATA: Record<string, { title: string; icon: string; desc: string }> = {
  require_stop_loss: {
    title: "Bắt buộc đặt Stop-loss",
    icon: "security",
    desc: "Bắt buộc có giá thoát vị thế (cắt lỗ) cho mỗi vị thế. Hạn chế sụt giảm tài khoản lớn bằng cách giới hạn rủi ro từng lệnh."
  },
  max_risk_per_trade: {
    title: "Rủi ro tối đa mỗi giao dịch",
    icon: "percent",
    desc: "Bảo vệ tài khoản bằng cách giới hạn nghiêm ngặt số vốn phân bổ chịu rủi ro trên mỗi lệnh giao dịch."
  },
  max_consecutive_losses: {
    title: "Chuỗi lệnh thua tối đa",
    icon: "history",
    desc: "Kích hoạt trạng thái 'Hạ nhiệt' (Cool Down) nhằm ngăn giao dịch trả thù và bốc đồng sau chuỗi lệnh thua liên tiếp."
  },
  max_fomo_score: {
    title: "Điểm FOMO tối đa cho phép",
    icon: "psychology",
    desc: "Được AI phân tích dựa trên tốc độ khớp lệnh và khoảng cách từ đường EMA. Ngăn mua đuổi bốc đồng theo sóng nóng."
  },
  max_trades_per_day: {
    title: "Số lệnh tối đa mỗi ngày",
    icon: "timer",
    desc: "Hạn chế giao dịch quá mức (over-trading) bằng cách giới hạn tổng số lệnh thực hiện trong một chu kỳ 24 giờ."
  },
  cooldown_after_loss: {
    title: "Thời gian nghỉ sau trade thua",
    icon: "hourglass_empty",
    desc: "Bắt buộc dừng giao dịch trong một khoảng thời gian (giờ) sau mỗi lệnh thua để ổn định tâm lý trước lệnh mới."
  },
  prevent_oversized_trade: {
    title: "Ngăn giao dịch khối lượng lớn",
    icon: "monitoring",
    desc: "Cảnh báo khi phát hiện quy mô lệnh tăng vọt bất thường so với lịch sử quy mô giao dịch trung bình trước đó."
  }
};

export const PersonalRules: React.FC = () => {
  // DB rules state & Current active draft rules state
  const [dbRules, setDbRules] = useState<Rule[]>([]);
  const [draftRules, setDraftRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Editing state for modal
  const [editingRule, setEditingRule] = useState<Rule | null>(null);
  const [editValue, setEditValue] = useState('');
  const [editError, setEditError] = useState('');

  // Toast Notification state
  const [showToast, setShowToast] = useState(false);

  // Fetch rules from Backend
  const fetchRules = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const response = await api.get('/rules');
      if (response.status === 200) {
        setDbRules(response.data);
        setDraftRules(JSON.parse(JSON.stringify(response.data))); // Deep copy for draft
      }
    } catch (err: any) {
      console.error('Failed to fetch rules', err);
      setErrorMsg(MessageProperties.CONNECTION_FAILED);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  // Handle Switch Toggle (draft state)
  const handleToggleChange = (ruleId: string) => {
    setDraftRules(prev =>
      prev.map(rule =>
        rule.id === ruleId ? { ...rule, is_active: !rule.is_active } : rule
      )
    );
  };

  // Open Edit Modal
  const openEditModal = (rule: Rule) => {
    setEditingRule(rule);
    setEditValue(rule.rule_value);
    setEditError('');
  };

  // Local Client-Side Validation
  const validateRuleValue = (type: string, value: string): string | null => {
    const trimmed = value.trim();
    if (!trimmed) {
      return 'Vui lòng nhập giá trị';
    }

    if (type === 'max_risk_per_trade') {
      const numeric = parseFloat(trimmed.replace('%', ''));
      if (isNaN(numeric) || numeric <= 0 || numeric >= 100) {
        return 'Tỉ lệ rủi ro phải là số lớn hơn 0 và nhỏ hơn 100';
      }
    } else if (['max_consecutive_losses', 'max_trades_per_day', 'cooldown_after_loss'].includes(type)) {
      const numeric = parseInt(trimmed, 10);
      if (isNaN(numeric) || numeric <= 0) {
        return 'Giá trị phải là số nguyên dương lớn hơn 0';
      }
    } else if (type === 'max_fomo_score') {
      const numeric = parseInt(trimmed, 10);
      if (isNaN(numeric) || numeric < 1 || numeric > 10) {
        return 'Điểm FOMO phải nằm trong khoảng từ 1 đến 10';
      }
    } else if (type === 'prevent_oversized_trade') {
      const numeric = parseInt(trimmed, 10);
      if (isNaN(numeric)) {
        return 'Vui lòng nhập một số nguyên hợp lệ';
      }
    } else if (type === 'require_stop_loss') {
      if (!['true', 'false', 'yes', 'no'].includes(trimmed.toLowerCase())) {
        return 'Giá trị phải là Yes/No hoặc True/False';
      }
    }
    return null;
  };

  // Confirm and Save Edit locally to Drafts
  const handleConfirmEdit = () => {
    if (!editingRule) return;
    const validationError = validateRuleValue(editingRule.rule_type, editValue);
    if (validationError) {
      setEditError(validationError);
      return;
    }

    let finalValue = editValue.trim();
    if (editingRule.rule_type === 'max_risk_per_trade' && !finalValue.endsWith('%')) {
      finalValue = `${parseFloat(finalValue.replace('%', ''))}%`;
    }

    setDraftRules(prev =>
      prev.map(rule =>
        rule.id === editingRule.id ? { ...rule, rule_value: finalValue } : rule
      )
    );
    setEditingRule(null);
  };

  // Discard all drafted changes
  const handleDiscardChanges = () => {
    setDraftRules(JSON.parse(JSON.stringify(dbRules)));
  };

  // Save all drafted changes to Server
  const handleSaveSettings = async () => {
    setSaving(true);
    setErrorMsg('');
    try {
      // Find rules that have changes
      for (const draft of draftRules) {
        const dbOrig = dbRules.find(r => r.id === draft.id);
        if (!dbOrig) continue;

        // 1. If value changed, call value endpoint
        if (draft.rule_value !== dbOrig.rule_value) {
          await api.put(`/rules/${draft.id}/value`, { rule_value: draft.rule_value });
        }

        // 2. If toggle state changed, call toggle endpoint
        if (draft.is_active !== dbOrig.is_active) {
          await api.put(`/rules/${draft.id}/toggle`);
        }
      }

      // Display Success Toast
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);

      // Refresh DB rules
      setDbRules(JSON.parse(JSON.stringify(draftRules)));
    } catch (err: any) {
      console.error('Failed to sync settings', err);
      if (err.response && err.response.data) {
        setErrorMsg(err.response.data.detail || MessageProperties.CONNECTION_FAILED);
      } else {
        setErrorMsg(MessageProperties.CONNECTION_FAILED);
      }
    } finally {
      setSaving(false);
    }
  };

  // Check if there are any changes in the draft rules compared to the db rules
  const hasChanges = JSON.stringify(dbRules) !== JSON.stringify(draftRules);

  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <span className={styles.spinner}></span>
        <p>Đang tải dữ liệu quy tắc...</p>
      </div>
    );
  }

  return (
    <div className={styles.wrapper}>
      {/* Warning Alert Banner */}
      <div className={`${styles.alertBanner} pulse`}>
        <span className="material-symbols-outlined">warning</span>
        <p>{MessageProperties.RULES_BANNER_WARNING}</p>
      </div>

      {errorMsg && (
        <div className={styles.errorAlert}>
          <span className="material-symbols-outlined">warning</span>
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Bento Layout Grid */}
      <div className={styles.bentoGrid}>
        {/* Left Side: Discipline Framework Card */}
        <section className={styles.frameworkCard}>
          <div className={styles.cardHeader}>
            <h3 className={styles.frameworkTitle}>{MessageProperties.RULES_BENTO_FRAMEWORK_TITLE}</h3>
            <p className={styles.frameworkDesc}>{MessageProperties.RULES_BENTO_FRAMEWORK_DESC}</p>
          </div>
          
          <div className={styles.scoreContainer}>
            <div className={styles.gauge}>
              <span className={styles.scoreNumber}>88</span>
            </div>
            <div className={styles.scoreText}>
              <p className={styles.scoreLabel}>{MessageProperties.RULES_BENTO_ADHERENCE_SCORE}</p>
              <p className={styles.scoreStatus}>{MessageProperties.RULES_BENTO_CONSISTENCY}</p>
            </div>
          </div>
        </section>

        {/* Right Side: Active Rules List */}
        <section className={styles.rulesList}>
          {draftRules.map(rule => {
            const meta = RULE_METADATA[rule.rule_type] || {
              title: rule.rule_type,
              icon: "gavel",
              desc: "Quy tắc kỷ luật giao dịch cá nhân."
            };

            return (
              <div 
                key={rule.id} 
                className={`${styles.ruleCard} ${rule.is_active ? styles.activeCard : styles.inactiveCard}`}
              >
                <div className={styles.ruleInfo}>
                  <div className={`${styles.iconBox} ${styles[meta.icon] || ''}`}>
                    <span className="material-symbols-outlined">{meta.icon}</span>
                  </div>
                  <div className={styles.textColumn}>
                    <div className={styles.titleRow}>
                      <h4 className={styles.ruleTitle}>{meta.title}</h4>
                      {rule.rule_type !== 'require_stop_loss' && (
                        <span className={styles.valueBadge}>{rule.rule_value}</span>
                      )}
                    </div>
                    <p className={styles.ruleDesc}>{meta.desc}</p>
                  </div>
                </div>

                <div className={styles.ruleActions}>
                  {rule.rule_type !== 'require_stop_loss' && (
                    <button 
                      className={styles.editBtn}
                      onClick={() => openEditModal(rule)}
                      title="Chỉnh sửa giá trị"
                      disabled={saving}
                    >
                      <span className="material-symbols-outlined">edit</span>
                    </button>
                  )}
                  <label className={styles.switch}>
                    <input 
                      type="checkbox" 
                      checked={rule.is_active}
                      onChange={() => handleToggleChange(rule.id)}
                      disabled={saving}
                    />
                    <span className={styles.slider}></span>
                  </label>
                </div>
              </div>
            );
          })}
        </section>
      </div>

      {/* Action Footer Buttons */}
      <footer className={styles.actionFooter}>
        <button 
          className={styles.discardBtn} 
          onClick={handleDiscardChanges}
          disabled={!hasChanges || saving}
        >
          {MessageProperties.RULES_BTN_DISCARD}
        </button>
        <button 
          className={styles.saveBtn} 
          onClick={handleSaveSettings}
          disabled={!hasChanges || saving}
        >
          {saving ? (
            <>
              <span className={styles.spinnerMini}></span>
              <span>Đang đồng bộ...</span>
            </>
          ) : (
            MessageProperties.RULES_BTN_SAVE
          )}
        </button>
      </footer>

      {/* Edit Value Modal Overlay */}
      {editingRule && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalCard}>
            <h3 className={styles.modalTitle}>{MessageProperties.RULES_EDIT_MODAL_TITLE}</h3>
            <p className={styles.modalLabel}>
              {MessageProperties.RULES_EDIT_MODAL_INPUT_LABEL} <strong>{RULE_METADATA[editingRule.rule_type]?.title}</strong>:
            </p>
            <input 
              type="text" 
              className={`${styles.modalInput} ${editError ? styles.errorInput : ''}`}
              value={editValue}
              onChange={(e) => {
                setEditValue(e.target.value);
                setEditError('');
              }}
              autoFocus
            />
            {editError && <span className={styles.modalError}>{editError}</span>}
            <div className={styles.modalActions}>
              <button className={styles.cancelBtn} onClick={() => setEditingRule(null)}>
                {MessageProperties.RULES_EDIT_MODAL_CANCEL}
              </button>
              <button className={styles.confirmBtn} onClick={handleConfirmEdit}>
                {MessageProperties.RULES_EDIT_MODAL_SAVE}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Success Toast Notification */}
      <div className={`${styles.toast} ${showToast ? styles.showToast : ''}`}>
        <span className="material-symbols-outlined">check_circle</span>
        <div className={styles.toastText}>
          <p className={styles.toastTitle}>{MessageProperties.RULES_TOAST_SUCCESS}</p>
          <p className={styles.toastDesc}>{MessageProperties.RULES_TOAST_SUCCESS_DESC}</p>
        </div>
      </div>
    </div>
  );
};

export default PersonalRules;
