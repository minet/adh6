import {MiniRouter, MiniRouterLoan} from "../api";

export const MODEL_LABELS: Record<MiniRouter.ModelEnum, string> = {
  beryl_giga: "Beryl (Giga)",
  ar750_fast: "AR750 (Fast)",
};

export const CONFIG_STATE_LABELS: Record<MiniRouter.ConfigStateEnum, string> = {
  pimped: $localize`:@@mini-router.config-state.pimped:Pimpé`,
  not_pimped: $localize`:@@mini-router.config-state.not-pimped:Pas pimpé`,
};

export const DEPOSIT_STATUS_LABELS: Record<
  MiniRouterLoan.DepositStatusEnum,
  string
> = {
  held: $localize`:@@mini-router.deposit.held:Encaissée`,
  refunded: $localize`:@@mini-router.deposit.refunded:Rendue`,
  kept: $localize`:@@mini-router.deposit.kept:Retenue`,
};

export const OVERDUE_LABEL = $localize`:@@mini-router.overdue:En retard`;

export interface DepositBadge {
  label: string;
  cssClass: string;
}

/** A returned loan whose deposit is still held must be settled. */
export function depositBadge(loan: MiniRouterLoan): DepositBadge {
  const status = loan.depositStatus ?? "held";
  if (status === "held" && loan.returnedAt) {
    return {
      label: $localize`:@@mini-router.deposit.to-refund:À rendre`,
      cssClass: "is-danger",
    };
  }
  const cssClasses: Record<MiniRouterLoan.DepositStatusEnum, string> = {
    held: "is-info",
    refunded: "is-success",
    kept: "is-warning",
  };
  return {
    label: DEPOSIT_STATUS_LABELS[status],
    cssClass: cssClasses[status],
  };
}
